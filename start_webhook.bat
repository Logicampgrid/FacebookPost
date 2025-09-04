@echo off
echo ===============================================
echo    FACEBOOK WEBHOOK AUTOMATION - WINDOWS
echo ===============================================
echo.

REM Se déplacer vers le répertoire du projet
cd /d "C:\FacebookPost"

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

REM Vérifier que ngrok est installé
ngrok version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: ngrok n'est pas installé ou pas dans le PATH
    echo Telecharger ngrok depuis: https://ngrok.com/download
    pause
    exit /b 1
)

echo ✅ Python detecte: 
python --version

echo ✅ Ngrok detecte:
ngrok version

echo.
echo 🚀 Demarrage de l'automatisation...
echo.

REM Lancer le script d'automatisation
python facebook_webhook_windows.py

echo.
echo 📋 Script termine
pause