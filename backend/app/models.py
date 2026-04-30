from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="teacher")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    students = relationship("Student", back_populates="assigned_class")
    sessions = relationship("Session", back_populates="associated_class")
    teacher = relationship("User", foreign_keys=[teacher_id])

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String, unique=True, index=True, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    photo_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assigned_class = relationship("Class", back_populates="students")
    face_images = relationship("FaceImage", back_populates="student", cascade="all, delete-orphan")
    attendance_logs = relationship("AttendanceLog", back_populates="student")

class FaceImage(Base):
    __tablename__ = "face_images"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String, nullable=False)
    uploadthing_key = Column(String, nullable=True)
    embedding_vector = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="face_images")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")

    associated_class = relationship("Class", back_populates="sessions")
    teacher = relationship("User")
    attendance_logs = relationship("AttendanceLog", back_populates="session")

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="Present")
    confidence = Column(Float, nullable=True)
    check_in_time = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="attendance_logs")
    student = relationship("Student", back_populates="attendance_logs")
