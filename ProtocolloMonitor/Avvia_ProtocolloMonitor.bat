@echo off
setlocal
title AVVIO PROTOCOLLOMONITOR
color 0A

echo ==========================================
echo        AVVIO PROTOCOLLOMONITOR
echo ==========================================
echo.

set "ROOT=C:\Users\fintu\Documents\GitHub\SoluzioniOperative\ProtocolloMonitor"
set "FRONTEND_DIR=%ROOT%\frontend"
set "PYTHON_DIR=%ROOT%\Python"

echo Cartella progetto:
echo %ROOT%
echo.

echo Avvio backend FastAPI...
start "ProtocolloMonitor - Backend FastAPI" cmd /k "powershell -NoProfile -NoExit -ExecutionPolicy Bypass -Command ""Set-Location -LiteralPath '%ROOT%'; python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"""

timeout /t 3 /nobreak > nul

echo Avvio frontend Vue/Vuetify...
start "ProtocolloMonitor - Frontend Vue" cmd /k "powershell -NoProfile -NoExit -ExecutionPolicy Bypass -Command ""Set-Location -LiteralPath '%FRONTEND_DIR%'; npm run dev"""

timeout /t 3 /nobreak > nul

echo Avvio server Flask Grisu...
start "ProtocolloMonitor - Server Flask Grisu" cmd /k "powershell -NoProfile -NoExit -ExecutionPolicy Bypass -Command ""Set-Location -LiteralPath '%PYTHON_DIR%'; python server_protocollo.py"""

timeout /t 2 /nobreak > nul

echo Avvio helper locale Apri con Word...
start "ProtocolloMonitor - Helper Apri con Word" cmd /k "powershell -NoProfile -NoExit -ExecutionPolicy Bypass -Command ""Set-Location -LiteralPath '%PYTHON_DIR%'; python open_word_helper.py"""

timeout /t 2 /nobreak > nul

echo Apertura browser...
start "" "http://localhost:5173"
start "" "http://127.0.0.1:8000/docs"
start "" "http://127.0.0.1:5000/ping"
start "" "http://127.0.0.1:8020/health"

echo.
echo Servizi richiesti avviati in finestre PowerShell separate.
echo Lascia aperte le finestre per mantenere attivi i servizi.
echo.
pause
