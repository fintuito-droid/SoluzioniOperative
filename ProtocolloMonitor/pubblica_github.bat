@echo off
title ProtocolloMonitor - Push GitHub

echo ==========================================
echo STATO FILE
echo ==========================================
git status

pause

git add .
git commit -m "Step 4 ProtocolloMonitor - Grisù dinamico UFFICIO GARE e cleanup database"
git push

pause