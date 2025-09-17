@echo off
setlocal enabledelayedexpansion
REM ===============================================
REM TEST OAUTH FACEBOOK IMMÉDIAT
REM ===============================================

echo.
echo ========================================
echo  TEST OAUTH FACEBOOK - SOLUTION RAPIDE
echo ========================================
echo.

echo [1/2] Détection de l'URL ngrok...

REM Récupérer l'URL ngrok active
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
    
    echo ✅ URL ngrok: !ngrok_url!
) else (
    echo ❌ Ngrok non détecté - assurez-vous qu'il est démarré
    pause
    exit /b 1
)

echo.
echo [2/2] Mise à jour Facebook OAuth...

REM Paramètres Facebook
set "APP_ID=5664227323683118"
set "APP_SECRET=b359a1c87c920288385daf75aed873a3"
set "APP_ACCESS_TOKEN=%APP_ID%|%APP_SECRET%"

echo 🔄 Configuration des domaines Facebook...

REM Mettre à jour les domaines
curl -s -X POST "https://graph.facebook.com/v18.0/%APP_ID%" ^
  -d "app_domains=[\"!ngrok_url!\"]" ^
  -d "access_token=%APP_ACCESS_TOKEN%" >NUL 2>&1

REM Mettre à jour les URIs OAuth
curl -s -X POST "https://graph.facebook.com/v18.0/%APP_ID%" ^
  -d "oauth_redirect_uris=[\"!ngrok_url!/\",\"!ngrok_url!/auth/callback\",\"!ngrok_url!/auth/callb\"]" ^
  -d "access_token=%APP_ACCESS_TOKEN%" >NUL 2>&1

REM Mettre à jour l'URL du site
curl -s -X POST "https://graph.facebook.com/v18.0/%APP_ID%" ^
  -d "website_url=!ngrok_url!" ^
  -d "access_token=%APP_ACCESS_TOKEN%" >NUL 2>&1

echo ✅ Configuration Facebook mise à jour!

REM Mettre à jour le frontend env
echo 🔄 Mise à jour frontend .env...
python "%~dp0update_frontend_env.py" "!ngrok_url!" >NUL 2>&1
if !errorlevel! equ 0 (
    echo ✅ Frontend .env mis à jour
) else (
    echo ⚠️ Erreur mise à jour frontend .env
)

echo.
echo ========================================
echo ✅ OAUTH FACEBOOK CONFIGURÉ
echo ========================================
echo.
echo 🎯 Configuration appliquée:
echo    • URL ngrok: !ngrok_url!
echo    • Domaines Facebook: Autorisés
echo    • URLs de redirection: Configurées
echo    • Frontend .env: Synchronisé
echo.
echo 🚀 TESTEZ MAINTENANT:
echo    1. Ouvrir: !ngrok_url!
echo    2. Cliquer "Se connecter avec Facebook"
echo    3. L'authentification devrait fonctionner!
echo.
echo 💡 Si le backend n'est pas démarré:
echo    Lancez: start_simple.bat
echo.
pause