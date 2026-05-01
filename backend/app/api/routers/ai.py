from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import base64
import cv2
import numpy as np
from datetime import datetime, timedelta

from app.api import deps
from app.core.database import get_db
from app import models
from app.ai.face_attendance import get_face_ai

router = APIRouter()

class RecognizeRequest(BaseModel):
    image: str  # base64 encoded image

class RecognizeResponse(BaseModel):
    success: bool
    recognized: bool
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    confidence: Optional[float] = None
    face_detection_confidence: Optional[float] = None
    status: Optional[str] = None
    message: Optional[str] = None
    is_unknown: Optional[bool] = None

class SaveFaceRequest(BaseModel):
    student_id: int
    image: str  # base64 encoded image

class SaveFaceResponse(BaseModel):
    success: bool
    message: str
    face_image_id: Optional[int] = None
    embedding_size: Optional[int] = None
    confidence: Optional[float] = None

def get_or_create_active_session(db: Session):
    """Get active session or create a default one"""
    session = db.query(models.Session).filter(
        models.Session.status == "active"
    ).first()
    
    if not session:
        # Get first class or create default
        db_class = db.query(models.Class).first()
        if not db_class:
            db_class = models.Class(
                name="General Attendance",
                description="Default class for live camera attendance"
            )
            db.add(db_class)
            db.commit()
            db.refresh(db_class)
        
        # Get first teacher or create default
        teacher = db.query(models.User).filter(models.User.role == "teacher").first()
        if not teacher:
            from app.core.security import get_password_hash
            teacher = models.User(
                username="admin",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                role="teacher"
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)
        
        session = models.Session(
            class_id=db_class.id,
            teacher_id=teacher.id,
            title="Live Camera Session",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=8),
            status="active"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    return session

def log_attendance(db: Session, student_id: int, session_id: int, confidence: float):
    """Log attendance if not already logged recently"""
    # Check if already logged in last 5 minutes
    five_mins_ago = datetime.utcnow() - timedelta(minutes=5)
    recent_log = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.student_id == student_id,
        models.AttendanceLog.session_id == session_id,
        models.AttendanceLog.check_in_time >= five_mins_ago
    ).first()
    
    if not recent_log:
        new_log = models.AttendanceLog(
            student_id=student_id,
            session_id=session_id,
            status="Present",
            confidence=float(confidence)
        )
        db.add(new_log)
        db.commit()
        return True
    return False

@router.post("/recognize", response_model=RecognizeResponse)
async def recognize_face(
    request: RecognizeRequest,
    db: Session = Depends(get_db)
):
    """
    Recognize face from base64 encoded image using comprehensive AI module
    """
    try:
        # Get AI instance
        face_ai = get_face_ai()
        
        # Process base64 image
        image = face_ai.process_base64_image(request.image)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Recognize face
        result = face_ai.recognize_face(image, db)
        
        if not result['success']:
            return RecognizeResponse(
                success=False,
                recognized=False,
                message=result['message']
            )
        
        if result['recognized']:
            # Get or create active session
            session = get_or_create_active_session(db)
            
            # Log attendance
            logged = log_attendance(db, result['student_id'], session.id, result['confidence'])
            
            return RecognizeResponse(
                success=True,
                recognized=True,
                student_id=str(result['student_id']),
                student_name=result['student_name'],
                confidence=result['confidence'],
                face_detection_confidence=result.get('face_detection_confidence'),
                status="Present" if logged else "Already Logged",
                message="Attendance recorded" if logged else "Already marked present"
            )
        else:
            return RecognizeResponse(
                success=True,
                recognized=False,
                confidence=result.get('confidence'),
                face_detection_confidence=result.get('face_detection_confidence'),
                is_unknown=result.get('is_unknown', False),
                message=result['message']
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recognition error: {str(e)}")

@router.post("/save-face", response_model=SaveFaceResponse)
async def save_student_face(
    request: SaveFaceRequest,
    db: Session = Depends(get_db)
):
    """
    Save student face image and generate embedding
    """
    try:
        # Verify student exists
        student = db.query(models.Student).filter(
            models.Student.id == request.student_id
        ).first()
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get AI instance
        face_ai = get_face_ai()
        
        # Process base64 image
        image = face_ai.process_base64_image(request.image)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Save face image and generate embedding
        result = face_ai.save_student_face_image(request.student_id, image, db)
        
        return SaveFaceResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving face: {str(e)}")

@router.get("/embeddings-stats")
async def get_embeddings_stats(db: Session = Depends(get_db)):
    """
    Get statistics about face embeddings in the database
    """
    try:
        face_ai = get_face_ai()
        stats = face_ai.get_student_embeddings_count(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@router.post("/update-threshold")
async def update_confidence_threshold(
    threshold: float,
    db: Session = Depends(get_db)
):
    """
    Update confidence threshold for face recognition
    """
    try:
        face_ai = get_face_ai()
        face_ai.update_confidence_threshold(threshold)
        return {"message": f"Confidence threshold updated to {threshold}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating threshold: {str(e)}")

@router.get("/system-info")
async def get_system_info():
    """
    Get AI system information
    """
    try:
        face_ai = get_face_ai()
        return {
            "device": face_ai.device,
            "confidence_threshold": face_ai.confidence_threshold,
            "face_size": face_ai.face_size,
            "models_loaded": {
                "yolo": face_ai.yolo_model is not None,
                "facenet": face_ai.facenet_model is not None,
                "mtcnn": face_ai.mtcnn is not None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system info: {str(e)}")
