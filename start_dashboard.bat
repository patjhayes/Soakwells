@echo off
title Soakwell Design Dashboard
echo.
echo 🌧️ Starting Soakwell Design Dashboard...
echo.
echo 📱 Dashboard will open at: http://localhost:8502
echo 🛑 Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"

REM Try to use virtual environment first
if exist ".venv\Scripts\python.exe" (
    echo Using virtual environment...
    ".venv\Scripts\python.exe" -m streamlit run soakwell_dashboard.py --server.port 8502
) else (
    echo Using system Python...
    python -m streamlit run soakwell_dashboard.py --server.port 8502
)

echo.
echo Dashboard stopped.
pause
