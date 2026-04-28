import os
from pathlib import Path

BASE_DIR = Path("backend")

def write_file(path, content):
    p = BASE_DIR / path
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

crud_content = """from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
from app.core.security import get_password_hash

# USERS
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    password_hash = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=password_hash,
        role=user.role if user.role in ["admin", "teacher"] else "teacher"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# STUDENTS
def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Student).offset(skip).limit(limit).all()

def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def get_student_by_email(db: Session, email: str):
    return db.query(models.Student).filter(models.Student.email == email).first()

def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db: Session, student_id: int, student: schemas.StudentCreate):
    db_student = get_student(db, student_id)
    if db_student:
        for key, value in student.model_dump().items():
            setattr(db_student, key, value)
        db.commit()
        db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: int):
    db_student = get_student(db, student_id)
    if db_student:
        db.delete(db_student)
        db.commit()
    return db_student

# CLASSES
def get_classes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Class).offset(skip).limit(limit).all()

def get_class(db: Session, class_id: int):
    return db.query(models.Class).filter(models.Class.id == class_id).first()

def create_class(db: Session, class_data: schemas.ClassCreate):
    db_class = models.Class(**class_data.model_dump())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

def update_class(db: Session, class_id: int, class_data: schemas.ClassCreate):
    db_class = get_class(db, class_id)
    if db_class:
        for key, value in class_data.model_dump().items():
            setattr(db_class, key, value)
        db.commit()
        db.refresh(db_class)
    return db_class

def delete_class(db: Session, class_id: int):
    db_class = get_class(db, class_id)
    if db_class:
        db.delete(db_class)
        db.commit()
    return db_class

# SESSIONS
def get_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Session).offset(skip).limit(limit).all()

def get_session(db: Session, session_id: int):
    return db.query(models.Session).filter(models.Session.id == session_id).first()

def create_session(db: Session, session_data: schemas.SessionCreate):
    db_session = models.Session(**session_data.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_session(db: Session, session_id: int, session_data: schemas.SessionCreate):
    db_session = get_session(db, session_id)
    if db_session:
        for key, value in session_data.model_dump().items():
            setattr(db_session, key, value)
        db.commit()
        db.refresh(db_session)
    return db_session

def delete_session(db: Session, session_id: int):
    db_session = get_session(db, session_id)
    if db_session:
        db.delete(db_session)
        db.commit()
    return db_session

# ATTENDANCE
def get_attendance(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AttendanceLog).offset(skip).limit(limit).all()

def create_attendance(db: Session, attendance: schemas.AttendanceCreate):
    db_attendance = models.AttendanceLog(**attendance.model_dump())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

# STATS
def get_dashboard_stats(db: Session):
    total_students = db.query(func.count(models.Student.id)).scalar()
    total_classes = db.query(func.count(models.Class.id)).scalar()
    total_sessions = db.query(func.count(models.Session.id)).scalar()
    total_attendance = db.query(func.count(models.AttendanceLog.id)).scalar()
    
    return {
        "total_students": total_students,
        "total_classes": total_classes,
        "total_sessions": total_sessions,
        "total_attendance": total_attendance
    }
"""

students_content = """from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_teacher_user
from app import crud, models, schemas

router = APIRouter()

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
"""

classes_content = """from fastapi import APIRouter, Depends, HTTPException, status
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
"""

sessions_content = """from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app import crud, schemas

router = APIRouter()

@router.get("/", response_model=list[schemas.SessionResponse])
def read_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sessions(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    return crud.create_session(db=db, session_data=session_data)

@router.put("/{session_id}", response_model=schemas.SessionResponse)
def update_session(session_id: int, session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    db_session = crud.update_session(db, session_id, session_data)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    db_session = crud.delete_session(db, session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return None
"""

attendance_content = """from fastapi import APIRouter, Depends, HTTPException, status
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
"""

stats_content = """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app import crud

router = APIRouter()

@router.get("/")
def get_dashboard_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)
"""

main_content = """from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api.routers import auth, students, attendance, classes, stats, sessions
from app.api import deps

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Smart Face Attendance System",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(students.router, prefix="/api/v1/students", tags=["students"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(classes.router, prefix="/api/v1/classes", tags=["classes"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(attendance.router, prefix="/api/v1/attendance", tags=["attendance"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(stats.router, prefix="/api/v1/dashboard/stats", tags=["stats"], dependencies=[Depends(deps.get_current_active_user)])

@app.get("/")
def root():
    return {"message": "Welcome to Smart Face Attendance System API"}
"""

write_file("app/crud.py", crud_content)
write_file("app/api/routers/students.py", students_content)
write_file("app/api/routers/classes.py", classes_content)
write_file("app/api/routers/sessions.py", sessions_content)
write_file("app/api/routers/attendance.py", attendance_content)
write_file("app/api/routers/stats.py", stats_content)
write_file("main.py", main_content)

# We also need to add 'sessions' to app/api/routers/__init__.py
init_path = BASE_DIR / "app/api/routers/__init__.py"
if init_path.exists():
    with open(init_path, "a") as f:
        f.write("\nfrom . import sessions\n")

print("Backend update complete.")
