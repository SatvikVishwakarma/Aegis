@echo off
echo =====================================
echo   Aegis Security Dashboard
echo   Starting Backend and Frontend...
echo =====================================
echo.

REM Start Backend in new window
echo Starting FastAPI Backend...
start "Aegis Backend" cmd /k "cd Server && uvicorn app:app --reload"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start Frontend in new window
echo Starting Next.js Frontend...
start "Aegis Frontend" cmd /k "cd Dashboard && npm run dev"

echo.
echo =====================================
echo   Aegis Dashboard is starting!
echo =====================================
echo.
echo Backend API: http://localhost:8000
echo API Docs:    http://localhost:8000/docs
echo Frontend:    http://localhost:3000
echo.
echo Login with: admin / password123
echo.
echo Press Ctrl+C in each window to stop
echo =====================================
