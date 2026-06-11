@echo off
echo Avvio Backend AIB 2026...
start "Backend AIB" cmd /k "cd /d C:\Users\fintu\Documents\GitHub\SoluzioniOperative\Servizi\backend && uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Avvio Frontend AIB 2026...
start "Frontend AIB" cmd /k "cd /d C:\Users\fintu\Documents\GitHub\SoluzioniOperative\Servizi\frontend && npm run dev"

echo Servizi avviati. Apri http://localhost:5173
