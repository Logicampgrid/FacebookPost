@echo off
setlocal enabledelayedexpansion
REM ===============================================
REM SCRIPT DE DÉMARRAGE SIMPLE - FacebookPost
REM ===============================================

echo.
echo =========================================
echo   DÉMARRAGE RAPIDE FACEBOOK POST
echo =========================================
echo.

echo [1/3] Démarrage du backend FastAPI...
start "Backend FastAPI" cmd /k "cd /d "%~dp0backend" && echo 🚀 Démarrage du serveur FastAPI... && python server.py"

echo ⏳ Attente du démarrage backend (8 secondes)...
timeout /t 8 /nobreak >NUL

echo.
echo [2/3] Configuration automatique Facebook OAuth...
echo 🔄 Mise à jour de la configuration Facebook avec ngrok...

REM Récupérer l'URL ngrok
set "ngrok_url="
for /f "delims=" %%i in ('curl -s http://127.0.0.1:4040/api/tunnels 2^>NUL') do set "ngrok_response=%%i"

echo !ngrok_response! | findstr "public_url" >NUL 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=4 delims=:," %%a in ('echo !ngrok_response! ^| findstr "public_url"') do (
        set "raw_url=%%a"
    )
    set "ngrok_url=!raw_url:"=!"
    set "ngrok_url=!ngrok_url: =!"
    
    if not "!ngrok_url:~0,8!"=="https://" (
        set "ngrok_url=https://!ngrok_url!"
    )
    
    echo ✅ URL ngrok détectée: !ngrok_url!
    
    REM Mettre à jour Facebook OAuth
    start /MIN cmd /c ""%~dp0update_facebook_config.bat""
    
    REM Mettre à jour frontend env
    python "%~dp0update_frontend_env.py" "!ngrok_url!" >NUL 2>&1
    
) else (
    echo ⚠️ URL ngrok non détectée
    set "ngrok_url=http://localhost:8001"
)

echo.
echo [3/3] Ouverture de l'application...

timeout /t 3 /nobreak >NUL

if defined ngrok_url (
    echo 🌐 Ouverture: !ngrok_url!
    start "" "!ngrok_url!"
) else (
    echo 🌐 Ouverture: http://localhost:8001
    start "" "http://localhost:8001"
)

echo.
echo =========================================
echo ✅ DÉMARRAGE TERMINÉ
echo =========================================
echo.
echo 📋 Services actifs:
echo    • 🌐 Ngrok: !ngrok_url!
echo    • 🚀 Backend: Fenêtre séparée
echo    • 🔐 Facebook OAuth: Configuré automatiquement
echo.
echo ⚠️ Gardez la fenêtre backend ouverte
echo.
pause
exit /b 0