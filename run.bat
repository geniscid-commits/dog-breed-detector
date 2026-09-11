@echo off
echo Starting Dog Breed Detector...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -q -r requirements.txt

REM Start Flask server
echo.
echo ================================================
echo Dog Breed Detector Server Started
echo ================================================
echo.
echo Backend: http://localhost:5000
echo Frontend: Open index.html in your browser
echo.
echo Press Ctrl+C to stop the server
echo.

python server.py
pause
