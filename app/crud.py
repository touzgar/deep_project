from sqlalchemy.orm import Session
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

def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

# CLASSES
def create_class(db: Session, class_data: schemas.ClassCreate):
    db_class = models.Class(**class_data.model_dump())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

# ATTENDANCE
def create_attendance(db: Session, attendance: schemas.AttendanceCreate):
    db_attendance = models.AttendanceLog(**attendance.model_dump())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def get_attendance(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AttendanceLog).offset(skip).limit(limit).all()

