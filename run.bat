@echo off
REM Startup script for LLM Quiz Solver (Windows)

echo Starting LLM Quiz Solver...

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
if not exist "venv\Scripts\playwright.exe" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo Installing Playwright browsers...
    playwright install chromium
)

REM Check if .env file exists
if not exist ".env" (
    echo No .env file found!
    echo Please create a .env file based on .env.example
    echo Run: copy .env.example .env
    echo Then edit .env with your actual credentials
    pause
    exit /b 1
)

REM Create temp directories
if not exist "temp" mkdir temp
if not exist "downloads" mkdir downloads

echo Starting application...
python app.py
