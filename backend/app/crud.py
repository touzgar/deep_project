from sqlalchemy.orm import Session
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
