@echo off
REM ===============================================
REM SCRIPT DE DÉMARRAGE TUNNEL - FacebookPost Application
REM Mode tunnel ngrok avec configuration Facebook OAuth
REM ===============================================

echo.
echo =========================================
echo   FACEBOOK POST - MODE TUNNEL NGROK
echo =========================================
echo.

REM Vérifier ngrok
ngrok version >NUL 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ngrok requis pour le mode tunnel
    echo 💡 Installez ngrok depuis https://ngrok.com/download
    pause
    exit /b 1
)

echo [1/4] Préparation du tunnel ngrok...

REM Arrêter ngrok existant
taskkill /f /im ngrok.exe >NUL 2>&1
timeout /t 2 /nobreak >NUL

REM Configurer le backend pour ngrok
cd backend
if exist ".env" (
    powershell -Command "(Get-Content .env) -replace 'ENABLE_NGROK=.*', 'ENABLE_NGROK=detect' | Set-Content .env" >NUL 2>&1
    echo ✅ Backend configuré pour ngrok
)
cd ..

echo.
echo [2/4] Démarrage du tunnel ngrok...
echo 🚀 Lancement de ngrok sur le port 8001...
start "Ngrok Tunnel - FacebookPost" cmd /c "ngrok http 8001 --log=stdout"

echo ⏳ Attente de l'initialisation du tunnel (15 secondes)...
timeout /t 15 /nobreak >NUL

REM Récupérer l'URL ngrok
echo 🔍 Récupération de l'URL ngrok...
set "ngrok_url="
set /a attempts=0

:get_ngrok_url
set /a attempts+=1
if %attempts% gtr 10 (
    echo ❌ Impossible de récupérer l'URL ngrok
    echo 💡 Vérifiez que ngrok fonctionne: http://127.0.0.1:4040
    pause
    exit /b 1
)

for /f "delims=" %%i in ('curl -s http://127.0.0.1:4040/api/tunnels 2^>NUL') do set "ngrok_response=%%i"
echo %ngrok_response% | findstr "public_url" >NUL 2>&1
if %errorlevel% neq 0 (
    echo ⏳ Tentative %attempts%/10: Tunnel en cours de création...
    timeout /t 3 /nobreak >NUL
    goto get_ngrok_url
)

REM Extraire l'URL (méthode simplifiée)
for /f "tokens=4 delims=:," %%a in ('echo %ngrok_response% ^| findstr "public_url"') do (
    set "ngrok_url=%%a"
)
set "ngrok_url=%ngrok_url:"=%"
set "ngrok_url=%ngrok_url: =%"
if not "%ngrok_url:~0,8%"=="https://" (
    set "ngrok_url=https://%ngrok_url%"
)

echo ✅ URL ngrok récupérée: %ngrok_url%

echo.
echo [3/4] Configuration des environnements...

REM Sauvegarder l'URL ngrok
echo %ngrok_url% > backend\ngrok_url.txt

REM Mettre à jour le frontend .env
cd frontend
if exist ".env" (
    powershell -Command "(Get-Content .env) -replace 'REACT_APP_BACKEND_URL=.*', 'REACT_APP_BACKEND_URL=%ngrok_url%' | Set-Content .env" >NUL 2>&1
    echo ✅ Frontend configuré pour ngrok: %ngrok_url%
)
cd ..

echo.
echo [4/4] Démarrage des services...

REM Démarrer le backend avec ngrok
echo 🚀 Démarrage du backend avec tunnel ngrok...
start "Backend FastAPI - FacebookPost (TUNNEL)" cmd /k "cd /d "%~dp0backend" && echo 🚀 FacebookPost Backend - Mode TUNNEL && echo 🌐 URL Publique: %ngrok_url% && echo 🔍 API Health: %ngrok_url%/api/health && echo 📱 Interface Ngrok: http://127.0.0.1:4040 && echo. && python server.py"

timeout /t 10 /nobreak >NUL

REM Démarrer le frontend
echo ⚛️ Démarrage du frontend...
start "Frontend React - FacebookPost (TUNNEL)" cmd /k "cd /d "%~dp0frontend" && echo ⚛️ FacebookPost Frontend - Mode TUNNEL && echo 🌐 Application: %ngrok_url% && echo 🔗 Backend API: %ngrok_url%/api/ && echo. && npm start"

timeout /t 15 /nobreak >NUL

echo.
echo =========================================
echo ✅ TUNNEL NGROK CONFIGURÉ AVEC SUCCÈS
echo =========================================
echo.
echo 🌐 URL Publique: %ngrok_url%
echo 📱 Accessible depuis n'importe où sur Internet
echo 🔍 Interface Ngrok: http://127.0.0.1:4040
echo.
echo 📋 Configuration Facebook OAuth requise:
echo    1. App Domains: %ngrok_url:~8%
echo    2. OAuth Redirect URIs: %ngrok_url%/auth/callback
echo    3. Webhooks URL: %ngrok_url%/api/webhook
echo.
echo 🎯 Ouverture de l'application...
start "" "%ngrok_url%"

echo.
echo 💡 Instructions importantes:
echo    • Configurez Facebook Developers avec la nouvelle URL
echo    • L'URL ngrok change à chaque redémarrage
echo    • Gardez toutes les fenêtres ouvertes
echo.
pause
exit /b 0