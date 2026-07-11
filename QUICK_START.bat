@echo off
REM Highway Pilot - Quick Start Setup Script (Windows Batch)
REM Run: QUICK_START.bat

setlocal enabledelayedexpansion
cls

echo.
echo 🛣️  Highway Pilot - Quick Start Setup
echo ======================================
echo.

REM Colors using color codes
REM 0A = Green, 0B = Cyan, 0E = Yellow, 0C = Red

REM Step 1: Backend Setup
echo.
echo [Backend Setup]
echo ===============

cd backend

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python not found. Please install Python 3.9+ from https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Create virtual environment
echo.
echo Creating Python virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo Installing Python dependencies...
echo (This may take a moment...)
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Setup environment
echo.
echo Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo.
    echo WARNING: Please edit .env with your API keys:
    echo   - OPENAI_API_KEY
    echo   - ANTHROPIC_API_KEY
    echo   - DATABASE_URL (optional)
    echo.
) else (
    echo .env already exists
)

echo.
echo ✓ Backend setup complete!
echo.

REM Step 2: Frontend Setup
echo [Frontend Setup]
echo ================
echo.

cd ..\pilot-web

REM Check if Node.js is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Node.js/npm not found. Please install from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo Installing Node dependencies...
echo (This may take a moment...)
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install Node dependencies
    pause
    exit /b 1
)

echo.
echo ✓ Frontend setup complete!
echo.

REM Step 3: Startup Instructions
echo [Startup Instructions]
echo =====================
echo.
echo To start the application, open TWO separate Command Prompt windows:
echo.
echo Terminal 1 - Backend:
echo   cd backend
echo   .venv\Scripts\activate.bat
echo   uvicorn app.main:app --reload --port 8000
echo.
echo Terminal 2 - Frontend:
echo   cd pilot-web
echo   npm run dev
echo.
echo Then open: http://localhost:5173
echo.

echo ========================================
echo ✓ Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Open backend\.env and add your API keys
echo 2. Follow the startup instructions above
echo 3. Open http://localhost:5173 in your browser
echo 4. Start using Highway Pilot!
echo.
echo For detailed information, see:
echo   - HIGHWAY_PILOT_SETUP.md - Full setup guide
echo   - README_HIGHWAY_PILOT.md - Project overview
echo   - DEVELOPER_GUIDE.md - How to extend
echo   - INDEX.md - Navigation guide
echo.
echo Happy coding! 🚀
echo.

pause
