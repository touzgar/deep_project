from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from pathlib import Path
import shutil

from app.core.database import get_db
from app.api.deps import get_current_teacher_user
from app import crud, models, schemas
from app.ai.face_attendance import get_face_ai
from app.services.uploadthing import get_uploadthing_service

router = APIRouter()

class AddFaceImageRequest(BaseModel):
    image: str  # base64 encoded image

class AddFaceImageResponse(BaseModel):
    success: bool
    message: str
    face_image_id: Optional[int] = None
    embedding_size: Optional[int] = None
    confidence: Optional[float] = None

class UploadPhotosResponse(BaseModel):
    success: bool
    message: str
    uploaded_count: int
    failed_count: int
    face_images: List[dict] = []
    errors: List[str] = []

@router.get("/", response_model=list[schemas.StudentResponse])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_students(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = crud.get_student_by_email(db, email=student.email)
    if db_student:
        raise HTTPException(status_code=400, detail="Student email already registered")
    return crud.create_student(db=db, student=student)

@router.put("/{student_id}", response_model=schemas.StudentResponse)
def update_student(student_id: int, student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = crud.update_student(db, student_id, student)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.delete_student(db, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return None

@router.post("/{student_id}/face-images", response_model=UploadPhotosResponse)
async def upload_student_face_images(
    student_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload multiple face images for a student"""
    # Check if student exists
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Create student directory
    student_dir = Path(f"uploads/students/{student_id}")
    student_dir.mkdir(parents=True, exist_ok=True)
    
    # Get services
    face_ai = get_face_ai()
    uploadthing = get_uploadthing_service()
    
    uploaded_count = 0
    failed_count = 0
    face_images = []
    errors = []
    
    for file in files:
        try:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                errors.append(f"{file.filename}: Invalid file type")
                failed_count += 1
                continue
            
            # Read file data
            file_data = await file.read()
            
            # Generate unique filename
            file_extension = Path(file.filename).suffix.lower()
            if not file_extension:
                file_extension = '.jpg'
            
            unique_filename = f"student_{student_id}_{uuid.uuid4().hex}{file_extension}"
            
            # Save locally first
            local_path = student_dir / unique_filename
            with open(local_path, "wb") as f:
                f.write(file_data)
            
            # Upload to UploadThing
            upload_result = uploadthing.upload_file(
                file_data=file_data,
                filename=unique_filename,
                content_type=file.content_type
            )
            
            # Process with AI
            import cv2
            import numpy as np
            
            # Convert bytes to OpenCV image
            nparr = np.frombuffer(file_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                errors.append(f"{file.filename}: Could not decode image")
                failed_count += 1
                continue
            
            # Save face image and generate embedding
            ai_result = face_ai.save_student_face_image(student_id, image, db)
            
            if ai_result['success']:
                # Update database record with UploadThing URL
                face_image = db.query(models.FaceImage).filter(
                    models.FaceImage.id == ai_result['face_image_id']
                ).first()
                
                if face_image and upload_result['success']:
                    face_image.image_path = upload_result['url']  # Use UploadThing URL
                    face_image.uploadthing_key = upload_result.get('key')
                    db.commit()
                
                face_images.append({
                    'id': ai_result['face_image_id'],
                    'filename': file.filename,
                    'url': upload_result.get('url') if upload_result['success'] else str(local_path),
                    'embedding_size': ai_result['embedding_size'],
                    'confidence': ai_result['confidence']
                })
                uploaded_count += 1
            else:
                errors.append(f"{file.filename}: {ai_result['message']}")
                failed_count += 1
                
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
            failed_count += 1
    
    return UploadPhotosResponse(
        success=uploaded_count > 0,
        message=f"Uploaded {uploaded_count} images, {failed_count} failed",
        uploaded_count=uploaded_count,
        failed_count=failed_count,
        face_images=face_images,
        errors=errors
    )

@router.post("/{student_id}/face-image", response_model=AddFaceImageResponse)
def add_student_face_image(
    student_id: int,
    request: AddFaceImageRequest,
    db: Session = Depends(get_db)
):
    """Add single face image for student from base64"""
    # Check if student exists
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        # Get AI instance and save face image
        face_ai = get_face_ai()
        image = face_ai.process_base64_image(request.image)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        result = face_ai.save_student_face_image(student_id, image, db)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        
        return AddFaceImageResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding face image: {str(e)}")

@router.get("/{student_id}/face-images")
def get_student_face_images(student_id: int, db: Session = Depends(get_db)):
    """Get all face images for a student"""
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    face_images = db.query(models.FaceImage).filter(
        models.FaceImage.student_id == student_id
    ).all()
    
    return {
        "student_id": student_id,
        "student_name": f"{student.first_name} {student.last_name}",
        "face_images_count": len(face_images),
        "face_images": [
            {
                "id": img.id,
                "image_path": img.image_path,
                "uploadthing_key": getattr(img, 'uploadthing_key', None),
                "has_embedding": img.embedding_vector is not None,
                "created_at": img.created_at
            }
            for img in face_images
        ]
    }

@router.delete("/{student_id}/face-images/{image_id}")
def delete_student_face_image(
    student_id: int,
    image_id: int,
    db: Session = Depends(get_db)
):
    """Delete a specific face image"""
    face_image = db.query(models.FaceImage).filter(
        models.FaceImage.id == image_id,
        models.FaceImage.student_id == student_id
    ).first()
    
    if not face_image:
        raise HTTPException(status_code=404, detail="Face image not found")
    
    try:
        # Delete from UploadThing if it has a key
        if hasattr(face_image, 'uploadthing_key') and face_image.uploadthing_key:
            uploadthing = get_uploadthing_service()
            uploadthing.delete_file(face_image.uploadthing_key)
        
        # Delete local file if it exists
        if face_image.image_path and os.path.exists(face_image.image_path):
            os.remove(face_image.image_path)
        
        # Delete from database
        db.delete(face_image)
        db.commit()
        
        return {"message": "Face image deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting face image: {str(e)}")
