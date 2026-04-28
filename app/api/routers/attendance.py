from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from fastapi.responses import Response
from app.core.database import get_db
from app.api.deps import get_current_teacher_user
from app import crud, models, schemas
from app.utils.export import generate_excel_report, generate_pdf_report
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.get("/", response_model=list[schemas.AttendanceResponse])
def read_attendance(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_teacher_user)):
    attendance_records = crud.get_attendance(db, skip=skip, limit=limit)
    return attendance_records

@router.post("/", response_model=schemas.AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_teacher_user)):
    return crud.create_attendance(db, attendance)

@router.get("/export", response_class=Response)
def export_attendance(
    format: str = Query(..., description="Format: pdf or excel"),
    class_id: Optional[int] = None,
    date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_teacher_user)
):
    query = db.query(models.AttendanceLog).join(models.Session).join(models.Student)
    
    class_info = "All Classes"
    if class_id:
        class_obj = db.query(models.ClassSession).filter(models.ClassSession.id == class_id).first()
        if class_obj:
            class_info = class_obj.course_name
        query = query.filter(models.Session.class_id == class_id)
        
    date_info = "All Dates"
    if date:
        date_info = date
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(models.Session.start_time >= datetime.combine(target_date, datetime.min.time()))
            query = query.filter(models.Session.start_time <= datetime.combine(target_date, datetime.max.time()))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
            
    records = query.all()
    
    data_dicts = []
    for r in records:
        data_dicts.append({
            "Student ID": r.student.student_id,
            "Name": f"{r.student.first_name} {r.student.last_name}",
            "Class": r.session.course.course_name if r.session and r.session.course else "N/A",
            "Date": r.session.start_time.strftime("%Y-%m-%d %H:%M") if r.session else "N/A",
            "Status": r.status
        })
        
    if not data_dicts:
        # Provide empty payload with correct headers
        data_dicts.append({
            "Student ID": "", "Name": "", "Class": "", "Date": "", "Status": ""
        })

    if format.lower() == "excel":
        file_bytes = generate_excel_report(data_dicts)
        return Response(
            content=file_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=attendance_report_{datetime.now().strftime('%Y%m%d')}.xlsx"}
        )
    elif format.lower() == "pdf":
        file_bytes = generate_pdf_report(data_dicts, class_info=class_info, date_info=date_info)
        return Response(
            content=file_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=attendance_report_{datetime.now().strftime('%Y%m%d')}.pdf"}
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'pdf' or 'excel'")

