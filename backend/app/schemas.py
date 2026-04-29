from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# USER schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "teacher"

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

# STUDENT schemas
class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    class_id: int
    student_id: Optional[str] = None
    photo_path: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    class_id: int
    student_id: Optional[str] = None
    photo_path: Optional[str] = None
    created_at: datetime
    class_name: Optional[str] = None  # For displaying class name
    class Config:
        from_attributes = True

# CLASS schemas
class ClassCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ClassResponse(ClassCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# SESSION schemas
class SessionCreate(BaseModel):
    class_id: int
    teacher_id: int
    title: str
    start_time: datetime
    end_time: datetime
    status: Optional[str] = "scheduled"

class SessionResponse(BaseModel):
    id: int
    class_id: int
    teacher_id: int
    title: str
    date: datetime
    start_time: datetime
    end_time: datetime
    status: str
    class_name: Optional[str] = None  # For displaying class name
    teacher_name: Optional[str] = None  # For displaying teacher name
    class Config:
        from_attributes = True

# ATTENDANCE schemas
class AttendanceCreate(BaseModel):
    session_id: int
    student_id: int
    status: str = "Present"
    confidence: Optional[float] = None

class AttendanceResponse(AttendanceCreate):
    id: int
    check_in_time: datetime
    student_name: Optional[str] = None  # Added for displaying student names
    class Config:
        from_attributes = True

# TOKEN schemas
class Token(BaseModel):
    access_token: str
    token_type: str

# DASHBOARD STATS schemas
class DayAttendance(BaseModel):
    name: str
    present: int
    absent: int

class WeekRate(BaseModel):
    name: str
    rate: float

class StatusCount(BaseModel):
    name: str
    value: int

class DashboardStatsResponse(BaseModel):
    totalStudents: int
    totalClasses: int
    totalSessions: int
    totalAttendance: int
    totalSessionsToday: int
    presentToday: int
    absentToday: int
    attendancePercentage: float
    weeklyAttendance: List[DayAttendance]
    monthlyAttendanceRate: List[WeekRate]
    presentVsAbsent: List[StatusCount]


