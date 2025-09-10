@echo off
setlocal enabledelayedexpansion

:: ===================================================================
:: SCRIPT DE DÉMARRAGE COMPLET FACEBOOKPOST - VERSION WINDOWS
:: ===================================================================
:: Ce script lance MongoDB, Backend, Frontend et Ngrok automatiquement
:: avec tolérance aux pannes et redémarrage automatique
:: ===================================================================

title FacebookPost - Démarrage Complet

:: Configuration des chemins
set "BASE_DIR=C:\FacebookPost"
set "BACKEND_DIR=%BASE_DIR%\backend"
set "FRONTEND_DIR=%BASE_DIR%\frontend"
set "LOGS_DIR=%BASE_DIR%\logs"
set "MONGO_EXE=C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe"
set "MONGO_DATA=C:\data\db"
set "LOG_FILE=%BASE_DIR%\start_full.log"

:: Créer le répertoire de logs s'il n'existe pas
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

:: Fonction de logging avec timestamp
:log
set "timestamp=%date% %time%"
echo [%timestamp%] %~1
echo [%timestamp%] %~1 >> "%LOG_FILE%"
goto :eof

:: Démarrage du script
call :log "🚀 ===== DÉMARRAGE FACEBOOKPOST ====="
call :log "📁 Répertoire base: %BASE_DIR%"
call :log "📋 Log principal: %LOG_FILE%"

:: ===================================================================
:: ÉTAPE 1: VÉRIFICATION DES PRÉREQUIS
:: ===================================================================
call :log "🔍 Vérification des prérequis..."

:: Vérifier Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log "❌ Node.js non trouvé! Installez Node.js depuis https://nodejs.org"
    pause
    exit /b 1
)
call :log "✅ Node.js détecté"

:: Vérifier Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log "❌ Python non trouvé! Installez Python depuis https://python.org"
    pause
    exit /b 1
)
call :log "✅ Python détecté"

:: Vérifier ngrok
ngrok version >nul 2>&1
if %errorlevel% neq 0 (
    call :log "❌ Ngrok non trouvé! Installez ngrok depuis https://ngrok.com"
    pause
    exit /b 1
)
call :log "✅ Ngrok détecté"

:: Vérifier MongoDB
if not exist "%MONGO_EXE%" (
    call :log "❌ MongoDB non trouvé à: %MONGO_EXE%"
    call :log "💡 Installez MongoDB 8.0 ou modifiez le chemin dans ce script"
    pause
    exit /b 1
)
call :log "✅ MongoDB détecté"

:: Créer le répertoire de données MongoDB
if not exist "%MONGO_DATA%" (
    call :log "📁 Création répertoire MongoDB: %MONGO_DATA%"
    mkdir "%MONGO_DATA%"
)

:: ===================================================================
:: ÉTAPE 2: GESTION MONGODB
:: ===================================================================
call :log "🗄️ Gestion MongoDB..."

:: Vérifier si MongoDB tourne déjà
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe" >NUL
if %errorlevel% equ 0 (
    call :log "✅ MongoDB déjà en cours d'exécution"
) else (
    call :log "🚀 Démarrage MongoDB..."
    start "MongoDB" /MIN "%MONGO_EXE%" --dbpath "%MONGO_DATA%"
    
    :: Attendre que MongoDB soit prêt
    call :log "⏳ Attente MongoDB (30 secondes max)..."
    set /a "mongo_timeout=30"
    :wait_mongo
    timeout /t 1 /nobreak >nul
    tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe" >NUL
    if %errorlevel% equ 0 (
        call :log "✅ MongoDB démarré avec succès"
        goto mongo_ready
    )
    set /a "mongo_timeout-=1"
    if %mongo_timeout% gtr 0 goto wait_mongo
    
    call :log "❌ Timeout MongoDB - continuons quand même"
)

:mongo_ready

:: ===================================================================
:: ÉTAPE 3: INSTALLATION DES DÉPENDANCES
:: ===================================================================
call :log "📦 Vérification des dépendances..."

:: Backend - Python
cd /d "%BACKEND_DIR%"
if not exist "venv" (
    call :log "🐍 Création environnement virtuel Python..."
    python -m venv venv
)

call :log "🔄 Activation environnement virtuel..."
call venv\Scripts\activate.bat

call :log "📥 Installation dépendances Python..."
pip install -r requirements.txt --quiet

:: Frontend - Node.js
cd /d "%FRONTEND_DIR%"
if not exist "node_modules" (
    call :log "📥 Installation dépendances Node.js..."
    npm install
) else (
    call :log "✅ Dépendances Node.js déjà installées"
)

:: Vérifier si le build existe
if not exist "build" (
    call :log "🏗️ Build du frontend..."
    npm run build
) else (
    call :log "✅ Build frontend existant"
)

:: ===================================================================
:: ÉTAPE 4: DÉMARRAGE BACKEND AVEC REDÉMARRAGE AUTOMATIQUE
:: ===================================================================
call :log "🌐 Démarrage backend avec tolérance aux pannes..."

cd /d "%BACKEND_DIR%"
call venv\Scripts\activate.bat

:: Script de redémarrage automatique backend
:restart_backend
call :log "🚀 Lancement backend (port 8001)..."

:: Lancer le backend et capturer son PID (simulé)
start "FacebookPost Backend" /MIN python server_windows.py

:: Attendre que le backend soit prêt
call :log "⏳ Attente backend (45 secondes max)..."
set /a "backend_timeout=45"
:wait_backend
timeout /t 1 /nobreak >nul
curl -s http://localhost:8001/api/health >nul 2>&1
if %errorlevel% equ 0 (
    call :log "✅ Backend opérationnel"
    goto backend_ready
)
set /a "backend_timeout-=1"
if %backend_timeout% gtr 0 goto wait_backend

call :log "⚠️ Backend pas encore prêt - continuons"

:backend_ready

:: ===================================================================
:: ÉTAPE 5: ATTENTE URL NGROK
:: ===================================================================
call :log "🌐 Attente URL ngrok (60 secondes max)..."

set /a "ngrok_timeout=60"
set "ngrok_url="

:wait_ngrok
timeout /t 1 /nobreak >nul

:: Vérifier si le fichier ngrok_url.txt existe
if exist "%BACKEND_DIR%\ngrok_url.txt" (
    set /p ngrok_url=<"%BACKEND_DIR%\ngrok_url.txt"
    if not "!ngrok_url!"=="" (
        call :log "✅ URL Ngrok obtenue: !ngrok_url!"
        goto ngrok_ready
    )
)

set /a "ngrok_timeout-=1"
if %ngrok_timeout% gtr 0 goto wait_ngrok

call :log "⚠️ Timeout ngrok - utilisation URL locale"
set "ngrok_url=http://localhost:8001"

:ngrok_ready

:: ===================================================================
:: ÉTAPE 6: DÉMARRAGE FRONTEND
:: ===================================================================
call :log "🎨 Démarrage frontend..."

cd /d "%FRONTEND_DIR%"

:: Mettre à jour le .env avec l'URL ngrok
echo REACT_APP_BACKEND_URL=!ngrok_url! > .env
echo DANGEROUSLY_DISABLE_HOST_CHECK=true >> .env
echo ESLINT_NO_DEV_ERRORS=true >> .env
echo HOST=0.0.0.0 >> .env
echo PORT=3000 >> .env

call :log "📝 Frontend .env mis à jour avec: !ngrok_url!"

:: Démarrer le frontend
start "FacebookPost Frontend" /MIN npm start

:: Attendre que le frontend soit prêt
call :log "⏳ Attente frontend (30 secondes max)..."
set /a "frontend_timeout=30"
:wait_frontend
timeout /t 2 /nobreak >nul
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    call :log "✅ Frontend opérationnel"
    goto frontend_ready
)
set /a "frontend_timeout-=1"
if %frontend_timeout% gtr 0 goto wait_frontend

call :log "⚠️ Frontend pas encore complètement prêt"

:frontend_ready

:: ===================================================================
:: ÉTAPE 7: OUVERTURE NAVIGATEUR
:: ===================================================================
call :log "🌐 Ouverture du navigateur..."

:: Ouvrir le navigateur sur l'URL ngrok (qui servira le frontend)
if not "!ngrok_url!"=="http://localhost:8001" (
    call :log "🚀 Ouverture: !ngrok_url!"
    start "" "!ngrok_url!"
) else (
    call :log "🚀 Ouverture: http://localhost:3000"
    start "" "http://localhost:3000"
)

:: ===================================================================
:: ÉTAPE 8: MONITORING ET REDÉMARRAGE AUTOMATIQUE
:: ===================================================================
call :log "👁️ Monitoring actif - redémarrage automatique en cas de crash"
call :log "📋 Appuyez sur Ctrl+C pour arrêter tous les services"
call :log "📊 Status: Backend=%ngrok_url% | Frontend=http://localhost:3000"

:: Boucle de monitoring
:monitor_loop
timeout /t 10 /nobreak >nul

:: Vérifier backend
curl -s http://localhost:8001/api/health >nul 2>&1
if %errorlevel% neq 0 (
    call :log "❌ Backend crashé - redémarrage..."
    taskkill /F /FI "WINDOWTITLE eq FacebookPost Backend" >nul 2>&1
    goto restart_backend
)

:: Vérifier frontend
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% neq 0 (
    call :log "❌ Frontend crashé - redémarrage..."
    taskkill /F /FI "WINDOWTITLE eq FacebookPost Frontend" >nul 2>&1
    cd /d "%FRONTEND_DIR%"
    start "FacebookPost Frontend" /MIN npm start
    call :log "🔄 Frontend redémarré"
)

:: Vérifier MongoDB
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe" >NUL
if %errorlevel% neq 0 (
    call :log "❌ MongoDB crashé - redémarrage..."
    start "MongoDB" /MIN "%MONGO_EXE%" --dbpath "%MONGO_DATA%"
    call :log "🔄 MongoDB redémarré"
)

goto monitor_loop

:: ===================================================================
:: NETTOYAGE EN CAS D'ARRÊT
:: ===================================================================
:cleanup
call :log "🛑 Arrêt des services..."
taskkill /F /FI "WINDOWTITLE eq FacebookPost Backend" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq FacebookPost Frontend" >nul 2>&1
taskkill /F /IM "ngrok.exe" >nul 2>&1
call :log "✅ Nettoyage terminé"
exit /b 0