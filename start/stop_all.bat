@echo off
echo =========================================
echo      ARRET SERVICES - FacebookPost
echo =========================================
echo.

echo 🛑 Arrêt de tous les services FacebookPost...

REM Arrêter les processus Python (backend)
echo Arrêt du backend...
taskkill /f /im python.exe >nul 2>&1

REM Arrêter les processus Node.js (si frontend en mode dev)
echo Arrêt du frontend...
taskkill /f /im node.exe >nul 2>&1

REM Arrêter MongoDB
echo Arrêt de MongoDB...
taskkill /f /im mongod.exe >nul 2>&1

echo.
echo ✅ Tous les services ont été arrêtés
echo.
pause