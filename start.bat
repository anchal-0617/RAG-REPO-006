@echo off

echo ==============================
echo Starting AskMyDocs Backend
echo ==============================

start "AskMyDocs Backend" cmd /k "python -m uvicorn Backend.main:Backend --reload"

timeout /t 3 /nobreak > nul

echo ==============================
echo Opening AskMyDocs Frontend
echo ==============================

start "" "frontend\index.html"

echo.
echo AskMyDocs started!
echo Backend: http://127.0.0.1:8000
echo.

pause