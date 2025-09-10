@echo off
setlocal enabledelayedexpansion

:: ===================================================================
:: SCRIPT DE REDÉMARRAGE BACKEND FACEBOOKPOST
:: ===================================================================
:: Redémarre uniquement le backend et ngrok avec logging
:: ===================================================================

title FacebookPost - Redémarrage Backend

:: Configuration
set "BASE_DIR=C:\FacebookPost"
set "BACKEND_DIR=%BASE_DIR%\backend"
set "LOG_FILE=%BASE_DIR%\start_full.log"

:: Fonction de logging
:log
set "timestamp=%date% %time%"
echo [%timestamp%] %~1
echo [%timestamp%] %~1 >> "%LOG_FILE%"
goto :eof

call :log "🔄 ===== REDÉMARRAGE BACKEND ====="

:: ===================================================================
:: ÉTAPE 1: ARRÊT SERVICES EXISTANTS
:: ===================================================================
call :log "🛑 Arrêt backend et ngrok existants..."

:: Arrêter backend
tasklist /FI "WINDOWTITLE eq FacebookPost Backend" | find "python" >nul
if %errorlevel% equ 0 (
    call :log "🛑 Arrêt backend existant..."
    taskkill /F /FI "WINDOWTITLE eq FacebookPost Backend" >nul 2>&1
    timeout /t 2 /nobreak >nul
)

:: Arrêter ngrok
tasklist /FI "IMAGENAME eq ngrok.exe" | find "ngrok" >nul
if %errorlevel% equ 0 (
    call :log "🛑 Arrêt ngrok existant..."
    taskkill /F /IM "ngrok.exe" >nul 2>&1
    timeout /t 3 /nobreak >nul
)

:: ===================================================================
:: ÉTAPE 2: DÉMARRAGE BACKEND
:: ===================================================================
call :log "🚀 Redémarrage backend..."

cd /d "%BACKEND_DIR%"

:: Vérifier environnement virtuel
if not exist "venv\Scripts\activate.bat" (
    call :log "❌ Environnement virtuel non trouvé!"
    call :log "💡 Exécutez start_full.bat pour installation complète"
    pause
    exit /b 1
)

:: Activer environnement
call venv\Scripts\activate.bat

:: Lancer backend
start "FacebookPost Backend" /MIN python server_windows.py

call :log "⏳ Attente backend (30 secondes max)..."

:: Attendre que le backend soit opérationnel
set /a "timeout=30"
:wait_backend
timeout /t 1 /nobreak >nul
curl -s http://localhost:8001/api/health >nul 2>&1
if %errorlevel% equ 0 (
    call :log "✅ Backend opérationnel"
    goto backend_ok
)
set /a "timeout-=1"
if %timeout% gtr 0 goto wait_backend

call :log "⚠️ Backend lent à démarrer - continuons"

:backend_ok

:: ===================================================================
:: ÉTAPE 3: ATTENTE URL NGROK
:: ===================================================================
call :log "🌐 Attente nouvelle URL ngrok (45 secondes max)..."

set /a "ngrok_timeout=45"
set "ngrok_url="

:wait_ngrok
timeout /t 1 /nobreak >nul

if exist "%BACKEND_DIR%\ngrok_url.txt" (
    set /p ngrok_url=<"%BACKEND_DIR%\ngrok_url.txt"
    if not "!ngrok_url!"=="" (
        call :log "✅ Nouvelle URL Ngrok: !ngrok_url!"
        goto ngrok_ok
    )
)

set /a "ngrok_timeout-=1"
if %ngrok_timeout% gtr 0 goto wait_ngrok

call :log "⚠️ Ngrok lent - vérifiez manuellement"
set "ngrok_url=http://localhost:8001"

:ngrok_ok

:: ===================================================================
:: ÉTAPE 4: MISE À JOUR FRONTEND
:: ===================================================================
call :log "🔄 Mise à jour configuration frontend..."

:: Mettre à jour .env frontend avec nouvelle URL
set "FRONTEND_ENV=%BASE_DIR%\frontend\.env"
if exist "%FRONTEND_ENV%" (
    echo REACT_APP_BACKEND_URL=!ngrok_url! > "%FRONTEND_ENV%"
    echo DANGEROUSLY_DISABLE_HOST_CHECK=true >> "%FRONTEND_ENV%"
    echo ESLINT_NO_DEV_ERRORS=true >> "%FRONTEND_ENV%"
    echo HOST=0.0.0.0 >> "%FRONTEND_ENV%"
    echo PORT=3000 >> "%FRONTEND_ENV%"
    call :log "✅ Frontend .env mis à jour"
)

:: ===================================================================
:: RÉSUMÉ
:: ===================================================================
call :log "✅ ===== REDÉMARRAGE BACKEND TERMINÉ ====="
call :log "🌐 Backend: http://localhost:8001"
call :log "🌐 Ngrok: !ngrok_url!"
call :log "💡 Le frontend utilisera automatiquement la nouvelle URL"

echo.
echo ========================================
echo   REDÉMARRAGE BACKEND TERMINÉ
echo ========================================
echo Backend local: http://localhost:8001
echo URL Ngrok: %ngrok_url%
echo Log complet: %LOG_FILE%
echo ========================================
echo.

pause