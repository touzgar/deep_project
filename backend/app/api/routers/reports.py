"""
Reports API Router
Handles attendance reports with filtering and export functionality
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, date
from typing import Optional, List
import io
import pandas as pd
from fpdf import FPDF

from app.core.database import get_db
from app import models
from pydantic import BaseModel

router = APIRouter()

class AttendanceReportItem(BaseModel):
    id: int
    student_id: int
    student_name: str
    student_email: str
    class_name: str
    session_title: str
    session_date: datetime
    status: str
    confidence: Optional[float]
    check_in_time: datetime

    class Config:
        from_attributes = True

class AttendanceReportResponse(BaseModel):
    total_records: int
    filtered_records: int
    attendance_data: List[AttendanceReportItem]
    summary: dict

@router.get("/attendance", response_model=AttendanceReportResponse)
async def get_attendance_report(
    class_id: Optional[int] = Query(None, description="Filter by class ID"),
    session_id: Optional[int] = Query(None, description="Filter by session ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by status (Present/Absent)"),
    student_id: Optional[int] = Query(None, description="Filter by student ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get attendance report with filters
    """
    try:
        # Build base query
        query = db.query(
            models.AttendanceLog.id,
            models.AttendanceLog.student_id,
            models.Student.first_name,
            models.Student.last_name,
            models.Student.email,
            models.Class.name.label('class_name'),
            models.Session.title.label('session_title'),
            models.Session.date.label('session_date'),
            models.AttendanceLog.status,
            models.AttendanceLog.confidence,
            models.AttendanceLog.check_in_time
        ).join(
            models.Student, models.AttendanceLog.student_id == models.Student.id
        ).join(
            models.Session, models.AttendanceLog.session_id == models.Session.id
        ).join(
            models.Class, models.Session.class_id == models.Class.id
        )

        # Apply filters
        filters = []
        
        if class_id:
            filters.append(models.Session.class_id == class_id)
        
        if session_id:
            filters.append(models.AttendanceLog.session_id == session_id)
        
        if start_date:
            filters.append(models.Session.date >= start_date)
        
        if end_date:
            filters.append(models.Session.date <= end_date)
        
        if status:
            filters.append(models.AttendanceLog.status == status)
        
        if student_id:
            filters.append(models.AttendanceLog.student_id == student_id)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Get total count
        total_records = db.query(models.AttendanceLog).count()
        filtered_records = query.count()
        
        # Apply pagination
        results = query.order_by(models.AttendanceLog.check_in_time.desc()).offset(skip).limit(limit).all()
        
        # Format results
        attendance_data = []
        for row in results:
            attendance_data.append(AttendanceReportItem(
                id=row.id,
                student_id=row.student_id,
                student_name=f"{row.first_name} {row.last_name}",
                student_email=row.email,
                class_name=row.class_name,
                session_title=row.session_title,
                session_date=row.session_date,
                status=row.status,
                confidence=row.confidence,
                check_in_time=row.check_in_time
            ))
        
        # Calculate summary statistics
        summary_query = query.with_entities(
            models.AttendanceLog.status,
            func.count(models.AttendanceLog.id).label('count')
        ).group_by(models.AttendanceLog.status).all()
        
        summary = {
            'total': filtered_records,
            'by_status': {row.status: row.count for row in summary_query},
            'present_percentage': 0.0
        }
        
        if filtered_records > 0:
            present_count = summary['by_status'].get('Present', 0)
            summary['present_percentage'] = round((present_count / filtered_records) * 100, 2)
        
        return AttendanceReportResponse(
            total_records=total_records,
            filtered_records=filtered_records,
            attendance_data=attendance_data,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@router.get("/attendance/export-excel")
async def export_attendance_excel(
    class_id: Optional[int] = Query(None),
    session_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    student_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Export attendance report to Excel
    """
    try:
        # Build query (same as get_attendance_report)
        query = db.query(
            models.AttendanceLog.id,
            models.Student.first_name,
            models.Student.last_name,
            models.Student.email,
            models.Class.name.label('class_name'),
            models.Session.title.label('session_title'),
            models.Session.date.label('session_date'),
            models.AttendanceLog.status,
            models.AttendanceLog.confidence,
            models.AttendanceLog.check_in_time
        ).join(
            models.Student, models.AttendanceLog.student_id == models.Student.id
        ).join(
            models.Session, models.AttendanceLog.session_id == models.Session.id
        ).join(
            models.Class, models.Session.class_id == models.Class.id
        )

        # Apply filters
        filters = []
        if class_id:
            filters.append(models.Session.class_id == class_id)
        if session_id:
            filters.append(models.AttendanceLog.session_id == session_id)
        if start_date:
            filters.append(models.Session.date >= start_date)
        if end_date:
            filters.append(models.Session.date <= end_date)
        if status:
            filters.append(models.AttendanceLog.status == status)
        if student_id:
            filters.append(models.AttendanceLog.student_id == student_id)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Get all results
        results = query.order_by(models.AttendanceLog.check_in_time.desc()).all()
        
        if not results:
            raise HTTPException(status_code=404, detail="No attendance records found")
        
        # Convert to DataFrame
        data = []
        for row in results:
            data.append({
                'ID': row.id,
                'Student Name': f"{row.first_name} {row.last_name}",
                'Email': row.email,
                'Class': row.class_name,
                'Session': row.session_title,
                'Session Date': row.session_date.strftime('%Y-%m-%d %H:%M') if row.session_date else '',
                'Status': row.status,
                'Confidence': f"{row.confidence:.2%}" if row.confidence else 'N/A',
                'Check-in Time': row.check_in_time.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Attendance Report', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Attendance Report']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        # Generate filename with timestamp
        filename = f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting to Excel: {str(e)}")

@router.get("/attendance/export-pdf")
async def export_attendance_pdf(
    class_id: Optional[int] = Query(None),
    session_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    student_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Export attendance report to PDF
    """
    try:
        # Build query (same as get_attendance_report)
        query = db.query(
            models.AttendanceLog.id,
            models.Student.first_name,
            models.Student.last_name,
            models.Student.email,
            models.Class.name.label('class_name'),
            models.Session.title.label('session_title'),
            models.Session.date.label('session_date'),
            models.AttendanceLog.status,
            models.AttendanceLog.confidence,
            models.AttendanceLog.check_in_time
        ).join(
            models.Student, models.AttendanceLog.student_id == models.Student.id
        ).join(
            models.Session, models.AttendanceLog.session_id == models.Session.id
        ).join(
            models.Class, models.Session.class_id == models.Class.id
        )

        # Apply filters
        filters = []
        if class_id:
            filters.append(models.Session.class_id == class_id)
        if session_id:
            filters.append(models.AttendanceLog.session_id == session_id)
        if start_date:
            filters.append(models.Session.date >= start_date)
        if end_date:
            filters.append(models.Session.date <= end_date)
        if status:
            filters.append(models.AttendanceLog.status == status)
        if student_id:
            filters.append(models.AttendanceLog.student_id == student_id)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Get all results
        results = query.order_by(models.AttendanceLog.check_in_time.desc()).all()
        
        if not results:
            raise HTTPException(status_code=404, detail="No attendance records found")
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Title
        pdf.cell(0, 10, 'Attendance Report', 0, 1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        pdf.ln(5)
        
        # Filters applied
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 8, 'Filters Applied:', 0, 1)
        pdf.set_font('Arial', '', 9)
        
        filter_text = []
        if class_id:
            filter_text.append(f"Class ID: {class_id}")
        if session_id:
            filter_text.append(f"Session ID: {session_id}")
        if start_date:
            filter_text.append(f"Start Date: {start_date}")
        if end_date:
            filter_text.append(f"End Date: {end_date}")
        if status:
            filter_text.append(f"Status: {status}")
        if student_id:
            filter_text.append(f"Student ID: {student_id}")
        
        if filter_text:
            pdf.cell(0, 6, ', '.join(filter_text), 0, 1)
        else:
            pdf.cell(0, 6, 'No filters applied (showing all records)', 0, 1)
        
        pdf.ln(5)
        
        # Summary statistics
        present_count = sum(1 for r in results if r.status == 'Present')
        absent_count = sum(1 for r in results if r.status == 'Absent')
        total_count = len(results)
        
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 8, 'Summary:', 0, 1)
        pdf.set_font('Arial', '', 9)
        pdf.cell(0, 6, f'Total Records: {total_count}', 0, 1)
        pdf.cell(0, 6, f'Present: {present_count} ({(present_count/total_count*100):.1f}%)', 0, 1)
        pdf.cell(0, 6, f'Absent: {absent_count} ({(absent_count/total_count*100):.1f}%)', 0, 1)
        pdf.ln(5)
        
        # Table header
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(50, 8, 'Student Name', 1, 0, 'C')
        pdf.cell(40, 8, 'Class', 1, 0, 'C')
        pdf.cell(40, 8, 'Session', 1, 0, 'C')
        pdf.cell(25, 8, 'Status', 1, 0, 'C')
        pdf.cell(35, 8, 'Check-in Time', 1, 1, 'C')
        
        # Table data
        pdf.set_font('Arial', '', 7)
        for row in results[:100]:  # Limit to 100 records for PDF
            student_name = f"{row.first_name} {row.last_name}"
            if len(student_name) > 25:
                student_name = student_name[:22] + '...'
            
            class_name = row.class_name[:20] if len(row.class_name) > 20 else row.class_name
            session_title = row.session_title[:20] if len(row.session_title) > 20 else row.session_title
            check_in = row.check_in_time.strftime('%Y-%m-%d %H:%M')
            
            pdf.cell(50, 6, student_name, 1, 0)
            pdf.cell(40, 6, class_name, 1, 0)
            pdf.cell(40, 6, session_title, 1, 0)
            pdf.cell(25, 6, row.status, 1, 0, 'C')
            pdf.cell(35, 6, check_in, 1, 1)
        
        if len(results) > 100:
            pdf.ln(5)
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 6, f'Note: Showing first 100 of {len(results)} records', 0, 1)
        
        # Generate PDF in memory
        pdf_output = io.BytesIO()
        pdf_bytes = pdf.output()
        pdf_output.write(pdf_bytes)
        pdf_output.seek(0)
        
        # Generate filename with timestamp
        filename = f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            pdf_output,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting to PDF: {str(e)}")

@router.get("/classes")
async def get_classes_for_filter(db: Session = Depends(get_db)):
    """Get all classes for filter dropdown"""
    classes = db.query(models.Class).all()
    return [{"id": c.id, "name": c.name} for c in classes]

@router.get("/sessions")
async def get_sessions_for_filter(
    class_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get sessions for filter dropdown"""
    query = db.query(models.Session)
    if class_id:
        query = query.filter(models.Session.class_id == class_id)
    sessions = query.order_by(models.Session.date.desc()).all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "date": s.date.isoformat() if s.date else None,
            "class_id": s.class_id
        }
        for s in sessions
    ]