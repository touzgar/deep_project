from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app import crud, schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.AttendanceResponse])
def read_attendance(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_attendance(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    return crud.create_attendance(db=db, attendance=attendance)
