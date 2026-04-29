@echo off
title Avvio ProtocolloMonitor
color 0A

echo ==========================================
echo        AVVIO PROTOCOLLOMONITOR
echo ==========================================
echo.

D:
cd "D:\OneDrive\FunTecVVF\Sviluppo\SoluzioniOperative\SoluzioniOperative\ProtocolloMonitor\Python"

echo Cartella corrente:
cd
echo.

echo Avvio server Python...
echo.

python server_protocollo.py

echo.
echo Processo terminato.
pause