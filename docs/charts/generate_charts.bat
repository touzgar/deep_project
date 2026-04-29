@echo off
echo ========================================
echo   Generating Model Comparison Charts
echo ========================================
echo.

echo Installing dependencies...
pip install -r requirements.txt
echo.

echo Generating charts...
python generate_charts.py
echo.

echo ========================================
echo   Charts generated successfully!
echo ========================================
echo.
echo Charts saved in: output/
echo.
pause
