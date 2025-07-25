@echo off
echo ========================================
echo Engineering Report Generator
echo North Fremantle Pedestrian Infrastructure
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or later
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "soakwell_dashboard.py" (
    echo ERROR: Required files not found
    echo Please run this from the project directory
    pause
    exit /b 1
)

REM Run the report launcher
echo Starting Engineering Report System...
echo.
python report_launcher.py

echo.
echo Report generation complete.
pause
