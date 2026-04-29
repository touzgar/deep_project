@echo off
echo ========================================
echo  Starting SmartAttend Backend Server
echo ========================================
echo.

cd backend

echo Checking if virtual environment exists...
if exist venv (
    echo Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo No virtual environment found. Using system Python.
)

echo.
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
