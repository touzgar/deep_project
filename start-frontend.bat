@echo off
echo ========================================
echo  Starting SmartAttend Frontend Server
echo ========================================
echo.

cd frontend

echo Installing dependencies (if needed)...
if not exist node_modules (
    echo Installing npm packages...
    call npm install
)

echo.
echo Starting development server...
echo Frontend will be available at http://localhost:5173
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

call npm run dev

pause
