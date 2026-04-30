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
    students = db.query(models.Student).offset(skip).limit(limit).all()
    # Add class name to each student
    result = []
    for student in students:
        student_dict = {
            "id": student.id,
            "student_id": student.student_id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "email": student.email,
            "class_id": student.class_id,
            "photo_path": student.photo_path,
            "created_at": student.created_at,
            "class_name": student.assigned_class.name if student.assigned_class else None
        }
        result.append(student_dict)
    return result

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
    classes = db.query(models.Class).offset(skip).limit(limit).all()
    # Add teacher name to each class
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
    sessions = db.query(models.Session).offset(skip).limit(limit).all()
    # Add class and teacher names
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
    from sqlalchemy.orm import joinedload
    
    # Query attendance logs with student information joined
    attendance_logs = db.query(models.AttendanceLog).options(
        joinedload(models.AttendanceLog.student)
    ).offset(skip).limit(limit).all()
    
    # Manually construct response with student_name
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

def create_attendance(db: Session, attendance: schemas.AttendanceCreate):
    db_attendance = models.AttendanceLog(**attendance.model_dump())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

# STATS
def get_dashboard_stats(db: Session):
    from datetime import datetime, timedelta
    
    # Basic counts
    total_students = db.query(func.count(models.Student.id)).scalar() or 0
    total_classes = db.query(func.count(models.Class.id)).scalar() or 0
    total_sessions = db.query(func.count(models.Session.id)).scalar() or 0
    total_attendance = db.query(func.count(models.AttendanceLog.id)).scalar() or 0
    
    # Today's date
    today = datetime.utcnow().date()
    
    # Today's sessions
    today_sessions = db.query(models.Session).filter(
        func.date(models.Session.start_time) == today
    ).all()
    total_sessions_today = len(today_sessions)
    
    # Today's attendance
    today_session_ids = [s.id for s in today_sessions]
    if today_session_ids:
        today_attendance = db.query(models.AttendanceLog).filter(
            models.AttendanceLog.session_id.in_(today_session_ids)
        ).all()
    else:
        today_attendance = []
    
    present_today = sum(1 for a in today_attendance if a.status == "Present")
    absent_today = total_students - present_today if total_students > 0 else 0
    attendance_percentage = round((present_today / total_students * 100), 2) if total_students > 0 else 0.0
    
    # Present vs Absent for today
    present_vs_absent = [
        {"name": "Present", "value": present_today},
        {"name": "Absent", "value": absent_today}
    ]
    
    # Weekly attendance (last 7 days)
    weekly_attendance = []
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    for i in range(6, -1, -1):  # Last 7 days
        target_date = today - timedelta(days=i)
        
        # Get sessions for this day
        day_sessions = db.query(models.Session).filter(
            func.date(models.Session.start_time) == target_date
        ).all()
        
        day_session_ids = [s.id for s in day_sessions]
        
        if day_session_ids:
            day_attendance = db.query(models.AttendanceLog).filter(
                models.AttendanceLog.session_id.in_(day_session_ids)
            ).all()
            
            day_present = sum(1 for a in day_attendance if a.status == "Present")
            day_absent = total_students - day_present if total_students > 0 else 0
        else:
            day_present = 0
            day_absent = 0
        
        # Get day name
        day_name = day_names[target_date.weekday()]
        
        weekly_attendance.append({
            "name": day_name,
            "present": day_present,
            "absent": day_absent
        })
    
    # Monthly attendance rate (last 4 weeks)
    monthly_attendance_rate = []
    
    for week_num in range(4, 0, -1):  # Last 4 weeks
        week_start = today - timedelta(days=week_num * 7)
        week_end = today - timedelta(days=(week_num - 1) * 7)
        
        # Get sessions for this week
        week_sessions = db.query(models.Session).filter(
            func.date(models.Session.start_time) >= week_start,
            func.date(models.Session.start_time) < week_end
        ).all()
        
        week_session_ids = [s.id for s in week_sessions]
        
        if week_session_ids:
            week_attendance = db.query(models.AttendanceLog).filter(
                models.AttendanceLog.session_id.in_(week_session_ids)
            ).all()
            
            week_present = sum(1 for a in week_attendance if a.status == "Present")
            week_total = len(week_attendance)
            week_rate = round((week_present / week_total * 100), 2) if week_total > 0 else 0.0
        else:
            week_rate = 0.0
        
        monthly_attendance_rate.append({
            "name": f"Week {5 - week_num}",
            "rate": week_rate
        })
    
    return {
        "totalStudents": total_students,
        "totalClasses": total_classes,
        "totalSessions": total_sessions,
        "totalAttendance": total_attendance,
        "totalSessionsToday": total_sessions_today,
        "presentToday": present_today,
        "absentToday": absent_today,
        "attendancePercentage": attendance_percentage,
        "weeklyAttendance": weekly_attendance,
        "monthlyAttendanceRate": monthly_attendance_rate,
        "presentVsAbsent": present_vs_absent
    }
