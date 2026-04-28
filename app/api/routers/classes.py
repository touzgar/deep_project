from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_teacher_user, get_current_admin_user
from app import crud, models, schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.ClassResponse])
def read_classes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_teacher_user)):
    classes = db.query(models.ClassSession).offset(skip).limit(limit).all()
    return classes

@router.post("/", response_model=schemas.ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(class_data: schemas.ClassCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    return crud.create_class(db, class_data)
