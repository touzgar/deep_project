from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_teacher_user
from app import crud, schemas, models

router = APIRouter()

# Teachers see only their sessions, Admins see all
@router.get("/", response_model=list[schemas.SessionResponse])
def read_sessions(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_teacher_user)
):
    if current_user.role == "admin":
        # Admin sees all sessions
        return crud.get_sessions(db, skip=skip, limit=limit)
    else:
        # Teacher sees only their own sessions
        sessions = db.query(models.Session).filter(
            models.Session.teacher_id == current_user.id
        ).offset(skip).limit(limit).all()
        
        # Format response
        result = []
        for session in sessions:
            session_dict = {
                "id": session.id,
                "class_id": session.class_id,
                "teacher_id": session.teacher_id,
                "title": session.title,
                "date": session.date,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "status": session.status,
                "class_name": session.associated_class.name if session.associated_class else None,
                "teacher_name": session.teacher.username if session.teacher else None
            }
            result.append(session_dict)
        return result

@router.post("/", response_model=schemas.SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    session_data: schemas.SessionCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_teacher_user)
):
    # Teachers can only create sessions for themselves
    if current_user.role == "teacher":
        if session_data.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only create sessions for themselves"
            )
        
        # Verify the class is assigned to this teacher
        class_obj = db.query(models.Class).filter(
            models.Class.id == session_data.class_id
        ).first()
        
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")
        
        if class_obj.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create sessions for classes assigned to you"
            )
    
    return crud.create_session(db=db, session_data=session_data)

@router.put("/{session_id}", response_model=schemas.SessionResponse)
def update_session(
    session_id: int, 
    session_data: schemas.SessionCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_teacher_user)
):
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Teachers can only edit their own sessions
    if current_user.role == "teacher" and db_session.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own sessions"
        )
    
    db_session = crud.update_session(db, session_id, session_data)
    return db_session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_teacher_user)
):
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Teachers can only delete their own sessions
    if current_user.role == "teacher" and db_session.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own sessions"
        )
    
    crud.delete_session(db, session_id)
    return None
