@echo off
REM ===============================================
REM Script d'arrêt FacebookPost Windows
REM ===============================================

echo.
echo ====================================
echo   Facebook Post - Arrêt Services
echo ====================================
echo.

echo 🛑 Arrêt des processus FacebookPost...

REM Arrêter les processus Python (backend)
echo 🔍 Recherche processus Python...
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *server_windows*" 2>nul | find /i "python.exe" >nul
if not errorlevel 1 (
    echo 🛑 Arrêt backend Python...
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq *server_windows*" >nul 2>&1
)

REM Arrêter les processus Node.js (frontend)
echo 🔍 Recherche processus Node.js...
tasklist /FI "IMAGENAME eq node.exe" 2>nul | find /i "node.exe" >nul
if not errorlevel 1 (
    echo 🛑 Arrêt frontend Node.js...
    taskkill /F /IM node.exe >nul 2>&1
)

REM Arrêter ngrok si en fonctionnement
echo 🔍 Recherche processus ngrok...
tasklist /FI "IMAGENAME eq ngrok.exe" 2>nul | find /i "ngrok.exe" >nul
if not errorlevel 1 (
    echo 🛑 Arrêt ngrok...
    taskkill /F /IM ngrok.exe >nul 2>&1
)

REM Libérer les ports
echo 🔧 Libération des ports...
netstat -ano | findstr :8001 >nul
if not errorlevel 1 (
    echo 🔓 Libération port 8001...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do taskkill /F /PID %%a >nul 2>&1
)

netstat -ano | findstr :3000 >nul
if not errorlevel 1 (
    echo 🔓 Libération port 3000...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ✅ Tous les services ont été arrêtés
echo 🔧 Ports 3000 et 8001 libérés
echo.

pause