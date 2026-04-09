@echo off
:: Set encoding to UTF-8
chcp 65001 >nul

echo ====================================================
echo    AI Knowledge Assistant - Startup Script
echo ====================================================

echo.
echo [1/2] Starting FastAPI Backend (Conda Environment: myenv)...
start "Backend API (Port 8000)" cmd /k "chcp 65001 >nul && call D:\software\anaconda3\Scripts\activate.bat myenv && uvicorn app.main:app --reload --port 8000"

echo [2/2] Starting Vue Frontend...
start "Frontend UI (Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo [OK] Startup commands sent to new windows!
echo ----------------------------------------------------
echo   Backend API Docs: http://127.0.0.1:8000/docs
echo   Frontend URL: Check the Frontend window (usually http://localhost:5173)
echo.
echo   Press any key to exit this window. The backend and frontend will continue running.
echo ====================================================
pause >nul
