@echo off
REM Live Camera Attendance System - Windows Setup Script

setlocal enabledelayedexpansion

REM Colors (limited in Windows CMD)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

REM Function to check if command exists
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo %ERROR% Python is required but not found
    exit /b 1
) else (
    echo %SUCCESS% Python found
)

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo %ERROR% Node.js is required but not found
    exit /b 1
) else (
    echo %SUCCESS% Node.js found
)

REM Parse command line argument
set "COMMAND=%1"
if "%COMMAND%"=="" set "COMMAND=install"

if "%COMMAND%"=="install" goto :install
if "%COMMAND%"=="start" goto :start
if "%COMMAND%"=="stop" goto :stop
if "%COMMAND%"=="test" goto :test
if "%COMMAND%"=="docker" goto :docker
if "%COMMAND%"=="clean" goto :clean
if "%COMMAND%"=="help" goto :help
goto :help

:install
echo %INFO% Starting Live Camera Attendance System installation...

REM Setup Backend
echo %INFO% Setting up backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo %INFO% Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo %INFO% Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Download YOLO model if not exists
if not exist "yolov8n.pt" (
    echo %INFO% Downloading YOLO model...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt' -OutFile 'yolov8n.pt'"
    echo %SUCCESS% YOLO model downloaded
) else (
    echo %SUCCESS% YOLO model already exists
)

REM Create .env file if not exists
if not exist ".env" (
    echo %INFO% Creating backend .env file...
    (
        echo DATABASE_URL=postgresql://admin:adminpassword@localhost:5432/attendance_db
        echo SECRET_KEY=your-secret-key-here-change-in-production
        echo ALGORITHM=HS256
    ) > .env
    echo %SUCCESS% Backend .env file created
)

cd ..

REM Setup Frontend
echo %INFO% Setting up frontend...
cd frontend

REM Install dependencies
echo %INFO% Installing Node.js dependencies...
npm install

REM Create .env file if not exists
if not exist ".env" (
    echo %INFO% Creating frontend .env file...
    echo VITE_API_URL=http://localhost:8000/api/v1 > .env
    echo %SUCCESS% Frontend .env file created
)

cd ..

echo %SUCCESS% Installation completed!
echo %INFO% Run 'setup.bat start' to start the services
goto :end

:start
echo %INFO% Starting services...

REM Start backend
echo %INFO% Starting backend server...
cd backend
call venv\Scripts\activate.bat
start "Backend Server" cmd /k "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
cd ..

REM Wait a bit for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend
echo %INFO% Starting frontend server...
cd frontend
start "Frontend Server" cmd /k "npm run dev -- --host 0.0.0.0"
cd ..

echo %SUCCESS% Services started!
echo %INFO% Backend: http://localhost:8000
echo %INFO% Frontend: http://localhost:5173
goto :end

:stop
echo %INFO% Stopping services...
taskkill /f /im "uvicorn.exe" 2>nul
taskkill /f /im "node.exe" 2>nul
echo %SUCCESS% Services stopped
goto :end

:test
echo %INFO% Running system tests...
cd backend
call venv\Scripts\activate.bat
cd ..
python test_live_camera.py
goto :end

:docker
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo %ERROR% Docker is not available
    goto :end
)

echo %INFO% Setting up Docker environment...

REM Ensure YOLO model exists
if not exist "backend\yolov8n.pt" (
    echo %INFO% Downloading YOLO model for Docker...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt' -OutFile 'backend\yolov8n.pt'"
)

REM Build and start services
echo %INFO% Building and starting Docker services...
docker-compose up -d

echo %SUCCESS% Docker services started!
echo %INFO% Frontend: http://localhost:3000
echo %INFO% Backend: http://localhost:8000
echo %INFO% Database: localhost:5432
goto :end

:clean
echo %INFO% Cleaning up...
taskkill /f /im "uvicorn.exe" 2>nul
taskkill /f /im "node.exe" 2>nul
del backend.log 2>nul
del frontend.log 2>nul
echo %SUCCESS% Cleanup completed
goto :end

:help
echo Live Camera Attendance System - Windows Setup Script
echo.
echo Usage: setup.bat [COMMAND]
echo.
echo Commands:
echo   install     - Install all dependencies and setup system
echo   start       - Start backend and frontend services
echo   stop        - Stop running services
echo   test        - Run system tests
echo   docker      - Setup and start with Docker
echo   clean       - Clean up temporary files and stop services
echo   help        - Show this help message
echo.
echo Examples:
echo   setup.bat install     # Full installation
echo   setup.bat start       # Start services
echo   setup.bat docker      # Use Docker
goto :end

:end
pause