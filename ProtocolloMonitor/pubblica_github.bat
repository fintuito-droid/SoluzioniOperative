@echo off
chcp 65001 >nul
title ProtocolloMonitor - Push GitHub

echo ==========================================
echo STATO FILE
echo ==========================================
git status

echo.
pause

echo ==========================================
echo AGGIUNTA FILE
echo ==========================================
git add .

echo ==========================================
echo COMMIT
echo ==========================================
git commit -m "Step 4 ProtocolloMonitor - Grisù dinamico UFFICIO GARE e cleanup database"

echo ==========================================
echo PUSH SU GITHUB
echo ==========================================
git push

echo.
echo Operazione completata con successo.
pause