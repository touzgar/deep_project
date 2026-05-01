from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_teacher_user
from app import crud, schemas, models
from sqlalchemy import func
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/", response_model=schemas.DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_teacher_user)
):
    if current_user.role == "admin":
        # Admin sees all stats
        return crud.get_dashboard_stats(db)
    else:
        # Teacher sees only their stats
        return get_teacher_dashboard_stats(db, current_user.id)

def get_teacher_dashboard_stats(db: Session, teacher_id: int):
    """Get dashboard stats for a specific teacher"""
    from datetime import datetime, timedelta
    
    # Get teacher's sessions
    teacher_sessions = db.query(models.Session).filter(
        models.Session.teacher_id == teacher_id
    ).all()
    
    session_ids = [s.id for s in teacher_sessions]
    
    # Get teacher's class IDs
    class_ids = list(set([s.class_id for s in teacher_sessions]))
    
    # Basic counts
    total_students = db.query(func.count(models.Student.id)).filter(
        models.Student.class_id.in_(class_ids) if class_ids else False
    ).scalar() or 0
    
    total_classes = len(class_ids)
    total_sessions = len(teacher_sessions)
    
    total_attendance = db.query(func.count(models.AttendanceLog.id)).filter(
        models.AttendanceLog.session_id.in_(session_ids) if session_ids else False
    ).scalar() or 0
    
    # Today's date
    today = datetime.utcnow().date()
    
    # Today's sessions
    today_sessions = [s for s in teacher_sessions if s.start_time.date() == today]
    total_sessions_today = len(today_sessions)
    today_session_ids = [s.id for s in today_sessions]
    
    # Today's attendance
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
    
    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        
        day_sessions = [s for s in teacher_sessions if s.start_time.date() == target_date]
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
        
        day_name = day_names[target_date.weekday()]
        
        weekly_attendance.append({
            "name": day_name,
            "present": day_present,
            "absent": day_absent
        })
    
    # Monthly attendance rate (last 4 weeks)
    monthly_attendance_rate = []
    
    for week_num in range(4, 0, -1):
        week_start = today - timedelta(days=week_num * 7)
        week_end = today - timedelta(days=(week_num - 1) * 7)
        
        week_sessions = [s for s in teacher_sessions 
                        if week_start <= s.start_time.date() < week_end]
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
