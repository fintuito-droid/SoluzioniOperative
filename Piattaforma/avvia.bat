@echo off
setlocal
title AVVIO PIATTAFORMA SOLUZIONIOPERATIVE
color 0A

echo ==============================================
echo    AVVIO PIATTAFORMA SOLUZIONIOPERATIVE
echo ==============================================
echo.
echo Backend:  ProtocolloMonitor :8000 - Servizi :8001 - XR33 :8002
echo Frontend: http://localhost:5173
echo.

set "ROOT=C:\Users\fintu\Documents\GitHub\SoluzioniOperative"

echo Avvio backend ProtocolloMonitor (porta 8000)...
start "SO - Backend ProtocolloMonitor :8000" cmd /k "cd /d %ROOT%\ProtocolloMonitor && python -m uvicorn backend.main:app --reload --port 8000"

echo Avvio backend Servizi (porta 8001)...
start "SO - Backend Servizi :8001" cmd /k "cd /d %ROOT%\Servizi\backend && uvicorn main:app --reload --port 8001"

echo Avvio backend XR33 (porta 8002)...
start "SO - Backend XR33 :8002" cmd /k "cd /d %ROOT%\XR33\backend && uvicorn main:app --reload --port 8002"

timeout /t 3 /nobreak > nul

echo Avvio server Flask Grisu (porta 5000, integrazione ProtocolloMonitor)...
start "SO - Server Flask Grisu :5000" cmd /k "cd /d %ROOT%\ProtocolloMonitor\Python && python server_protocollo.py"

echo Avvio helper Apri con Word (porta 8020, integrazione ProtocolloMonitor)...
start "SO - Helper Word :8020" cmd /k "cd /d %ROOT%\ProtocolloMonitor\Python && python open_word_helper.py"

timeout /t 2 /nobreak > nul

echo Avvio frontend piattaforma (porta 5173)...
start "SO - Frontend Piattaforma :5173" cmd /k "cd /d %ROOT%\Piattaforma\frontend && npm run dev"

timeout /t 4 /nobreak > nul

echo Apertura browser...
start "" "http://localhost:5173"

echo.
echo Piattaforma avviata. Lascia aperte le finestre per mantenere attivi i servizi.
echo Login sviluppo: admin / admin123
echo.
pause
