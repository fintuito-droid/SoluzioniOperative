@echo off
title Avvio ProtocolloMonitor
echo ==========================================
echo AVVIO PROTOCOLLOMONITOR
echo ==========================================

echo.
echo [1] Avvio backend FastAPI...
start "Backend FastAPI" powershell -NoExit -Command "cd 'C:\Users\fintu\Documents\GitHub\SoluzioniOperative\ProtocolloMonitor'; python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo.
echo [2] Avvio frontend Vue/Vuetify...
start "Frontend Vue" powershell -NoExit -Command "cd 'C:\Users\fintu\Documents\GitHub\SoluzioniOperative\ProtocolloMonitor\Frontend'; npm run dev"

timeout /t 3 /nobreak >nul

echo.
echo [3] Avvio server Flask Grisù...
start "Server Flask Grisu" powershell -NoExit -Command "cd 'C:\Users\fintu\Documents\GitHub\SoluzioniOperative\ProtocolloMonitor\Python'; python server_protocollo.py"

timeout /t 3 /nobreak >nul

echo.
echo [4] Build interfaccia Grisù...
start "Build Grisu" powershell -NoExit -Command "cd 'C:\Users\fintu\Documents\GitHub\SoluzioniOperative\ProtocolloMonitor\Estensione\grisu-v2'; npm run build"

timeout /t 5 /nobreak >nul

echo.
echo [5] Apertura browser...

start "" "http://127.0.0.1:8000/protocollo-monitor/protocolli"
start "" "http://localhost:5173/protocollo-monitor/protocolli"
start "" "http://127.0.0.1:5000/ping"
start "" "https://protocollo.dipvvf.it"

echo.
echo ==========================================
echo AVVIO COMPLETATO
echo ==========================================
echo.
pause