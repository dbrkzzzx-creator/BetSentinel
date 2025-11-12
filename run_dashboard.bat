@echo off
echo ========================================
echo Starting BetSentinel Dashboard
echo ========================================
echo.

cd /d D:\AI\BetSentinel

echo [1/2] Starting Flask backend on port 5000...
call venv\Scripts\activate
start "BetSentinel Backend" cmd /k "python app.py"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Next.js frontend on port 3000...
cd frontend
start "BetSentinel Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo Dashboard started!
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo Automation: http://localhost:3000/automation
echo ========================================
echo.
echo Press any key to exit this window (servers will keep running)...
pause >nul

