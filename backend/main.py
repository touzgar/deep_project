from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api.routers import auth, students, attendance, classes, stats, sessions, ai, reports
from app.api import deps

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Smart Face Attendance System",
    version="1.0.0"
)

# CORS Configuration - MUST be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(students.router, prefix="/api/v1/students", tags=["students"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(classes.router, prefix="/api/v1/classes", tags=["classes"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(attendance.router, prefix="/api/v1/attendance", tags=["attendance"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(stats.router, prefix="/api/v1/dashboard/stats", tags=["stats"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"], dependencies=[Depends(deps.get_current_active_user)])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"], dependencies=[Depends(deps.get_current_active_user)])

@app.get("/")
def root():
    return {"message": "Welcome to Smart Face Attendance System API"}

@app.get("/test-cors")
def test_cors():
    return {"status": "CORS is working!", "origin_allowed": "http://localhost:5173"}

# Debug: Print registered routes
print(f"Total routes registered: {len(app.routes)}")
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"  - {route.path}")
