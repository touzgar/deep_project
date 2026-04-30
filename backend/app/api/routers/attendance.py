from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_teacher_user
from app import crud, schemas, models

router = APIRouter()

# Teachers see only attendance from their sessions, Admins see all
@router.get("/", response_model=list[schemas.AttendanceResponse])
def read_attendance(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_teacher_user)
):
    if current_user.role == "admin":
        # Admin sees all attendance
        return crud.get_attendance(db, skip=skip, limit=limit)
    else:
        # Teacher sees only attendance from their sessions
        teacher_session_ids = db.query(models.Session.id).filter(
            models.Session.teacher_id == current_user.id
        ).all()
        
        session_ids = [sid[0] for sid in teacher_session_ids]
        
        if not session_ids:
            return []
        
        # Get attendance logs from teacher's sessions
        attendance_logs = db.query(models.AttendanceLog).filter(
            models.AttendanceLog.session_id.in_(session_ids)
        ).offset(skip).limit(limit).all()
        
        # Format response
        results = []
        for log in attendance_logs:
            log_dict = {
                "id": log.id,
                "session_id": log.session_id,
                "student_id": log.student_id,
                "status": log.status,
                "confidence": log.confidence,
                "check_in_time": log.check_in_time,
                "student_name": f"{log.student.first_name} {log.student.last_name}" if log.student else "Unknown Student"
            }
            results.append(log_dict)
        
        return results

@router.post("/", response_model=schemas.AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(
    attendance: schemas.AttendanceCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_teacher_user)
):
    # Verify session belongs to teacher (if teacher)
    if current_user.role == "teacher":
        session = db.query(models.Session).filter(
            models.Session.id == attendance.session_id
        ).first()
        
        if not session or session.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only mark attendance for your own sessions"
            )
    
    return crud.create_attendance(db=db, attendance=attendance)
