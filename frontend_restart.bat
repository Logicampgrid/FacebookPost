@echo off
setlocal enabledelayedexpansion

:: ===================================================================
:: SCRIPT DE REDÉMARRAGE FRONTEND FACEBOOKPOST
:: ===================================================================
:: Redémarre uniquement le frontend React
:: ===================================================================

title FacebookPost - Redémarrage Frontend

:: Configuration
set "BASE_DIR=C:\FacebookPost"
set "FRONTEND_DIR=%BASE_DIR%\frontend"
set "BACKEND_DIR=%BASE_DIR%\backend"
set "LOG_FILE=%BASE_DIR%\start_full.log"

:: Fonction de logging
:log
set "timestamp=%date% %time%"
echo [%timestamp%] %~1
echo [%timestamp%] %~1 >> "%LOG_FILE%"
goto :eof

call :log "🎨 ===== REDÉMARRAGE FRONTEND ====="

:: ===================================================================
:: ÉTAPE 1: ARRÊT FRONTEND EXISTANT
:: ===================================================================
call :log "🛑 Arrêt frontend existant..."

tasklist /FI "WINDOWTITLE eq FacebookPost Frontend" | find "node" >nul
if %errorlevel% equ 0 (
    call :log "🛑 Arrêt processus frontend..."
    taskkill /F /FI "WINDOWTITLE eq FacebookPost Frontend" >nul 2>&1
    timeout /t 3 /nobreak >nul
)

:: Arrêter tous les processus Node.js sur port 3000
netstat -ano | findstr ":3000" >nul
if %errorlevel% equ 0 (
    call :log "🛑 Libération port 3000..."
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

:: ===================================================================
:: ÉTAPE 2: RÉCUPÉRATION URL BACKEND
:: ===================================================================
call :log "🔍 Récupération URL backend..."

set "ngrok_url=http://localhost:8001"

:: Essayer de lire l'URL ngrok
if exist "%BACKEND_DIR%\ngrok_url.txt" (
    set /p ngrok_url=<"%BACKEND_DIR%\ngrok_url.txt"
    call :log "✅ URL backend trouvée: !ngrok_url!"
) else (
    call :log "⚠️ Fichier ngrok_url.txt non trouvé - utilisation localhost"
)

:: ===================================================================
:: ÉTAPE 3: MISE À JOUR CONFIGURATION
:: ===================================================================
call :log "📝 Mise à jour configuration frontend..."

cd /d "%FRONTEND_DIR%"

:: Créer/mettre à jour .env
echo REACT_APP_BACKEND_URL=!ngrok_url! > .env
echo DANGEROUSLY_DISABLE_HOST_CHECK=true >> .env
echo ESLINT_NO_DEV_ERRORS=true >> .env
echo HOST=0.0.0.0 >> .env
echo PORT=3000 >> .env

call :log "✅ Fichier .env mis à jour"

:: ===================================================================
:: ÉTAPE 4: VÉRIFICATION DÉPENDANCES
:: ===================================================================
call :log "📦 Vérification dépendances..."

if not exist "node_modules" (
    call :log "📥 Installation dépendances manquantes..."
    npm install
) else (
    call :log "✅ Dépendances présentes"
)

:: Vérifier/reconstruire si nécessaire
if not exist "build" (
    call :log "🏗️ Reconstruction build..."
    npm run build
) else (
    call :log "✅ Build présent"
)

:: ===================================================================
:: ÉTAPE 5: DÉMARRAGE FRONTEND
:: ===================================================================
call :log "🚀 Démarrage frontend..."

start "FacebookPost Frontend" /MIN npm start

:: Attendre que le frontend soit prêt
call :log "⏳ Attente frontend (45 secondes max)..."

set /a "timeout=45"
:wait_frontend
timeout /t 2 /nobreak >nul

:: Vérifier port 3000
netstat -an | findstr ":3000" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    call :log "✅ Frontend en écoute sur port 3000"
    goto frontend_ready
)

set /a "timeout-=1"
if %timeout% gtr 0 goto wait_frontend

call :log "⚠️ Frontend lent à démarrer"

:frontend_ready

:: Attendre réponse HTTP
call :log "🔍 Test réponse HTTP..."
set /a "http_timeout=30"
:wait_http
timeout /t 1 /nobreak >nul

curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    call :log "✅ Frontend répond aux requêtes HTTP"
    goto http_ok
)

set /a "http_timeout-=1"
if %http_timeout% gtr 0 goto wait_http

call :log "⚠️ Frontend pas complètement prêt"

:http_ok

:: ===================================================================
:: ÉTAPE 6: OUVERTURE NAVIGATEUR
:: ===================================================================
call :log "🌐 Ouverture navigateur..."

:: Ouvrir sur l'URL ngrok si disponible, sinon localhost
if not "!ngrok_url!"=="http://localhost:8001" (
    call :log "🚀 Ouverture: !ngrok_url!"
    start "" "!ngrok_url!"
) else (
    call :log "🚀 Ouverture: http://localhost:3000"
    start "" "http://localhost:3000"
)

:: ===================================================================
:: RÉSUMÉ
:: ===================================================================
call :log "✅ ===== REDÉMARRAGE FRONTEND TERMINÉ ====="
call :log "🎨 Frontend: http://localhost:3000"
call :log "🌐 Backend: !ngrok_url!"

echo.
echo ========================================
echo   REDÉMARRAGE FRONTEND TERMINÉ
echo ========================================
echo Frontend: http://localhost:3000
echo Backend: %ngrok_url%
echo Log complet: %LOG_FILE%
echo ========================================
echo.
echo Le navigateur va s'ouvrir automatiquement...

pause