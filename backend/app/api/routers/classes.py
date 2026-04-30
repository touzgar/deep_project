from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_admin_user, get_current_teacher_user
from app import crud, schemas, models

router = APIRouter()

# Teachers see only their classes, Admins see all
@router.get("/", response_model=list[schemas.ClassResponse])
def read_classes(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_teacher_user)
):
    if current_user.role == "admin":
        # Admin sees all classes
        return crud.get_classes(db, skip=skip, limit=limit)
    else:
        # Teacher sees only classes assigned to them
        classes = db.query(models.Class).filter(
            models.Class.teacher_id == current_user.id
        ).offset(skip).limit(limit).all()
        
        # Format response
        result = []
        for cls in classes:
            class_dict = {
                "id": cls.id,
                "name": cls.name,
                "description": cls.description,
                "teacher_id": cls.teacher_id,
                "created_at": cls.created_at,
                "teacher_name": cls.teacher.username if cls.teacher else None
            }
            result.append(class_dict)
        return result

# Only ADMIN can create classes
@router.post("/", response_model=schemas.ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    class_data: schemas.ClassCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    # Check if class name already exists
    existing = db.query(models.Class).filter(models.Class.name == class_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Class name already exists")
    return crud.create_class(db=db, class_data=class_data)

# Only ADMIN can update classes
@router.put("/{class_id}", response_model=schemas.ClassResponse)
def update_class(
    class_id: int, 
    class_data: schemas.ClassCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_class = crud.update_class(db, class_id, class_data)
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class

# Only ADMIN can delete classes
@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(
    class_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    db_class = crud.delete_class(db, class_id)
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return None
