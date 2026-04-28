from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app import crud, schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.ClassResponse])
def read_classes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_classes(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(class_data: schemas.ClassCreate, db: Session = Depends(get_db)):
    # Note: Could check if class name already exists
    return crud.create_class(db=db, class_data=class_data)

@router.put("/{class_id}", response_model=schemas.ClassResponse)
def update_class(class_id: int, class_data: schemas.ClassCreate, db: Session = Depends(get_db)):
    db_class = crud.update_class(db, class_id, class_data)
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class

@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(class_id: int, db: Session = Depends(get_db)):
    db_class = crud.delete_class(db, class_id)
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return None
