@echo off
REM ===============================================
REM Test de la solution OAuth Facebook automatique
REM ===============================================

echo.
echo ========================================
echo  TEST SOLUTION OAUTH FACEBOOK
echo ========================================
echo.

echo [1/3] Vérification de l'URL ngrok active...

REM Tester la détection de l'URL ngrok
for /f "delims=" %%i in ('curl -s http://127.0.0.1:4040/api/tunnels 2^>NUL') do set "ngrok_response=%%i"

echo %ngrok_response% | findstr "public_url" >NUL 2>&1
if %errorlevel% neq 0 (
    echo ❌ Aucune URL ngrok détectée
    echo 💡 Assurez-vous que ngrok est démarré sur le port 8001
    echo.
    echo Pour démarrer ngrok : ngrok http 8001
    pause
    exit /b 1
)

REM Extraire l'URL ngrok
for /f "tokens=4 delims=:," %%a in ('echo %ngrok_response% ^| findstr "public_url"') do (
    set "raw_url=%%a"
)

set "NGROK_URL=%raw_url:"=%"
set "NGROK_URL=%NGROK_URL: =%"

if not "%NGROK_URL:~0,8%"=="https://" (
    if not "%NGROK_URL:~0,7%"=="http://" (
        set "NGROK_URL=https://%NGROK_URL%"
    )
)

echo ✅ URL ngrok détectée: %NGROK_URL%

echo.
echo [2/3] Test de l'endpoint de santé du backend...

REM Tester si le backend répond
curl -s "%NGROK_URL%/api/health" >NUL 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend accessible via ngrok
) else (
    echo ⚠️ Backend non accessible via ngrok
    echo 💡 Assurez-vous que le backend FastAPI est démarré
)

echo.
echo [3/3] Exécution de la mise à jour Facebook...

REM Lancer la mise à jour Facebook OAuth
call "%~dp0update_facebook_config.bat"

echo.
echo ========================================
echo ✅ TEST TERMINÉ
echo ========================================
echo.
echo 🔧 Actions effectuées:
echo    • Détection automatique de l'URL ngrok
echo    • Vérification de l'accessibilité du backend  
echo    • Mise à jour de la configuration Facebook OAuth
echo.
echo 🌐 URL de test: %NGROK_URL%
echo.
echo 💡 Pour tester l'authentification Facebook:
echo    1. Ouvrir: %NGROK_URL%
echo    2. Cliquer sur "Se connecter avec Facebook"
echo    3. L'authentification devrait maintenant fonctionner
echo.
echo 📋 En cas de problème:
echo    • Vérifiez les logs du backend FastAPI
echo    • Consultez la Facebook Developers Console
echo    • Assurez-vous que l'app Facebook est en mode développement
echo.
pause