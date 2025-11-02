@echo off
echo ========================================
echo   Aegis Security Dashboard
echo   Setup Script
echo ========================================
echo.

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.9+
    pause
    exit /b 1
)
echo ✓ Python found
echo.

echo [2/3] Installing Backend Dependencies...
cd Server
pip install -r ../requirments.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo ✓ Backend dependencies installed
echo.

echo [3/3] Installing Frontend Dependencies...
cd Dashboard
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install Node.js dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo ✓ Frontend dependencies installed
echo.

echo ========================================
echo   Setup Complete! 🎉
echo ========================================
echo.
echo Next steps:
echo   1. Run: start.bat
echo   2. Open: http://localhost:3000
echo   3. Login: admin / password123
echo.
echo Or run manually:
echo   Terminal 1: cd Server ^&^& uvicorn app:app --reload
echo   Terminal 2: cd Dashboard ^&^& npm run dev
echo.
pause
