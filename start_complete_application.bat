@echo off
REM ===============================================
REM SCRIPT DE DÉMARRAGE COMPLET - FacebookPost Application
REM VERSION MISE À JOUR - Détection automatique ngrok
REM Lance ngrok (si disponible), backend et frontend
REM ===============================================

echo.
echo =========================================
echo   DÉMARRAGE FACEBOOK POST APPLICATION
echo   Détection automatique du mode
echo =========================================
echo.

REM Vérifier que nous sommes dans le bon répertoire
if not exist "backend\server.py" (
    echo ❌ Erreur: Fichier server.py non trouvé dans backend\
    echo 💡 Assurez-vous d'exécuter ce script depuis le répertoire racine du projet
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo ❌ Erreur: Fichier package.json non trouvé dans frontend\
    echo 💡 Assurez-vous d'exécuter ce script depuis le répertoire racine du projet
    pause
    exit /b 1
)

echo [1/5] Vérification des prérequis...

REM Vérifier Python
python --version >NUL 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo 💡 Installez Python depuis https://python.org
    pause
    exit /b 1
)
echo ✅ Python détecté

REM Vérifier Node.js/npm
node --version >NUL 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js n'est pas installé ou pas dans le PATH
    echo 💡 Installez Node.js depuis https://nodejs.org
    pause
    exit /b 1
)
echo ✅ Node.js détecté

REM Vérifier si ngrok est disponible
set "NGROK_AVAILABLE=false"
ngrok version >NUL 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ngrok détecté - Mode tunnel externe disponible
    set "NGROK_AVAILABLE=true"
) else (
    echo ⚠️ Ngrok non installé - Mode local uniquement
    echo 💡 Pour installer ngrok: https://ngrok.com/download
)

echo.
echo [2/5] Sélection du mode de fonctionnement...

if "%NGROK_AVAILABLE%"=="true" (
    echo 🤔 Ngrok est disponible. Quel mode souhaitez-vous ?
    echo.
    echo    1. Mode TUNNEL (ngrok) - Accès depuis Internet
    echo    2. Mode LOCAL - Accès depuis cet ordinateur uniquement
    echo.
    choice /c 12 /m "Votre choix"
    if errorlevel 2 goto local_mode
    if errorlevel 1 goto tunnel_mode
) else (
    echo ℹ️ Mode LOCAL automatiquement sélectionné (ngrok non disponible)
    goto local_mode
)

:tunnel_mode
echo.
echo 🌐 MODE TUNNEL SÉLECTIONNÉ - Accès Internet
echo.
call "%~dp0start_complete_application_tunnel.bat"
exit /b %errorlevel%

:local_mode
echo.
echo 🏠 MODE LOCAL SÉLECTIONNÉ - Accès local uniquement
echo.

REM Configuration pour mode local
echo [3/5] Configuration de l'environnement local...

REM Configuration .env backend pour mode local
cd backend
if exist ".env" (
    powershell -Command "(Get-Content .env) -replace 'ENABLE_NGROK=.*', 'ENABLE_NGROK=false' | Set-Content .env" >NUL 2>&1
    echo ✅ Backend configuré en mode local
)
cd ..

REM Configuration .env frontend pour mode local
cd frontend
if exist ".env" (
    powershell -Command "(Get-Content .env) -replace 'REACT_APP_BACKEND_URL=.*', 'REACT_APP_BACKEND_URL=http://localhost:8001' | Set-Content .env" >NUL 2>&1
    echo ✅ Frontend configuré pour backend local
)
cd ..

echo http://localhost:8001 > backend\ngrok_url.txt
echo ✅ Configuration locale appliquée

echo.
echo [4/5] Préparation des dépendances...

REM Installation des dépendances backend
echo 🔄 Vérification des dépendances Python...
cd backend
pip install -q -r requirements.txt >NUL 2>&1
if %errorlevel% neq 0 (
    pip install -q --user -r requirements.txt >NUL 2>&1
)
echo ✅ Dépendances Python prêtes
cd ..

REM Installation des dépendances frontend
echo 🔄 Vérification des dépendances Node.js...
cd frontend
if not exist "node_modules" (
    echo 📦 Installation des dépendances (peut prendre quelques minutes)...
    npm install --silent >NUL 2>&1
)
echo ✅ Dépendances Node.js prêtes
cd ..

echo.
echo [5/5] Démarrage des services...

REM Arrêter les processus existants
taskkill /f /im python.exe /fi "WINDOWTITLE eq *FacebookPost*" >NUL 2>&1
taskkill /f /im node.exe /fi "WINDOWTITLE eq *FacebookPost*" >NUL 2>&1
timeout /t 2 /nobreak >NUL

REM Démarrer le backend
echo 🚀 Démarrage du backend FastAPI...
start "Backend FastAPI - FacebookPost (LOCAL)" cmd /k "cd /d "%~dp0backend" && echo 🚀 FacebookPost Backend - Mode LOCAL && echo 🌐 API: http://localhost:8001 && echo 🔍 Health: http://localhost:8001/api/health && echo. && python server.py"

REM Attendre le backend
echo ⏳ Initialisation du backend...
timeout /t 10 /nobreak >NUL

REM Démarrer le frontend
echo ⚛️ Démarrage du frontend React...
start "Frontend React - FacebookPost (LOCAL)" cmd /k "cd /d "%~dp0frontend" && echo ⚛️ FacebookPost Frontend - Mode LOCAL && echo 🌐 Interface: http://localhost:3000 && echo 🔗 API Backend: http://localhost:8001 && echo. && npm start"

REM Attendre le frontend
echo ⏳ Initialisation du frontend...
timeout /t 15 /nobreak >NUL

echo.
echo =========================================
echo ✅ APPLICATION DÉMARRÉE AVEC SUCCÈS
echo =========================================
echo.
echo 📋 Services actifs (Mode LOCAL):
echo    • Backend API: http://localhost:8001
echo    • Frontend App: http://localhost:3000
echo    • MongoDB: Actif automatiquement
echo.
echo 🎯 Ouverture de l'application...
start "" "http://localhost:3000"

echo.
echo 💡 Instructions:
echo    • L'application s'ouvre dans votre navigateur
echo    • Gardez les fenêtres de commande ouvertes
echo    • Accès limité à cet ordinateur (mode local)
echo.
echo 🌐 Pour un accès Internet, relancez et choisissez le mode TUNNEL
echo.
pause
exit /b 0