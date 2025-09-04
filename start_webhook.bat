@echo off
chcp 65001 >nul
title Facebook Webhook Automation - Windows GUI

echo ===============================================
echo    FACEBOOK WEBHOOK AUTOMATION - WINDOWS
echo ===============================================
echo.

REM Se déplacer vers le répertoire du projet
if not exist "C:\FacebookPost" (
    echo ❌ ERREUR: Répertoire C:\FacebookPost non trouvé
    echo.
    echo Placez ce script dans C:\FacebookPost\
    echo.
    pause
    exit /b 1
)

cd /d "C:\FacebookPost"

REM Vérifier que Python 3.11+ est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR: Python n'est pas installé ou pas dans le PATH
    echo.
    echo Téléchargez Python 3.11+ depuis: https://python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Vérifier la version Python
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python détecté: %PYTHON_VERSION%

REM Vérifier que ngrok est installé
ngrok version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR: ngrok n'est pas installé ou pas dans le PATH
    echo.
    echo Téléchargez ngrok depuis: https://ngrok.com/download
    echo Extrayez ngrok.exe dans un dossier du PATH ou dans C:\FacebookPost\
    echo.
    pause
    exit /b 1
)

echo ✅ Ngrok détecté: 
ngrok version

REM Vérifier que le script GUI existe
if not exist "facebook_webhook_windows_gui.py" (
    echo ❌ ERREUR: facebook_webhook_windows_gui.py non trouvé
    echo.
    echo Assurez-vous que le script est dans C:\FacebookPost\
    echo.
    pause
    exit /b 1
)

echo.
echo 🚀 Lancement de l'interface graphique...
echo.

REM Supprimer les anciens logs
if exist "webhook_log.txt" del "webhook_log.txt"

REM Installer les dépendances si nécessaire
echo 📦 Vérification des dépendances Python...
pip install requests psutil --quiet

REM Lancer le script GUI
python facebook_webhook_windows_gui.py

REM Attendre avant de fermer si erreur
if errorlevel 1 (
    echo.
    echo ❌ Le script s'est terminé avec une erreur
    pause
)

echo.
echo 📋 Script terminé
pause