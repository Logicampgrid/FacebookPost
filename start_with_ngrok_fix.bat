@echo off
REM ===============================================
REM SCRIPT DE DÉMARRAGE AVEC CORRECTION NGROK
REM Résout le problème de page blanche ngrok
REM ===============================================

echo.
echo =========================================
echo   CORRECTION NGROK - FacebookPost
echo =========================================
echo.

REM Vérifier que nous sommes dans le bon répertoire
if not exist "backend\server.py" (
    echo ❌ Erreur: Fichier server.py non trouvé dans backend\
    echo 💡 Assurez-vous d'exécuter ce script depuis le répertoire racine du projet
    pause
    exit /b 1
)

echo [1/6] Arrêt des processus existants...

REM Arrêter les processus existants
taskkill /f /im python.exe /fi "WINDOWTITLE eq *FacebookPost*" >NUL 2>&1
taskkill /f /im node.exe /fi "WINDOWTITLE eq *FacebookPost*" >NUL 2>&1
taskkill /f /im ngrok.exe >NUL 2>&1
timeout /t 3 /nobreak >NUL

echo [2/6] Configuration de l'environnement local temporaire...

REM Configuration .env backend pour mode local temporaire
cd backend
if exist ".env" (
    powershell -Command "(Get-Content .env) -replace 'WEBHOOK_URL=.*', 'WEBHOOK_URL=http://localhost:8001' | Set-Content .env" >NUL 2>&1
    echo ✅ Backend configuré temporairement en mode local
)
cd ..

REM Configuration .env frontend pour mode local temporaire
cd frontend
if exist ".env" (
    powershell -Command "(Get-Content .env) -replace 'REACT_APP_BACKEND_URL=.*', 'REACT_APP_BACKEND_URL=http://localhost:8001' | Set-Content .env" >NUL 2>&1
    echo ✅ Frontend configuré temporairement en mode local
)
cd ..

echo [3/6] Démarrage du backend...

REM Démarrer le backend
start "Backend FastAPI - FacebookPost (CORRECTION)" cmd /k "cd /d "%~dp0backend" && echo 🚀 FacebookPost Backend - Mode CORRECTION && echo 🌐 API: http://localhost:8001 && echo 🔍 Health: http://localhost:8001/api/health && echo. && python server.py"

echo ⏳ Initialisation du backend...
timeout /t 8 /nobreak >NUL

echo [4/6] Test de l'API backend...

REM Tester l'API backend
curl -s http://localhost:8001/api/health >NUL 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API opérationnel
) else (
    echo ❌ Backend API non accessible
    echo 💡 Vérifiez la fenêtre backend pour les erreurs
    pause
    exit /b 1
)

echo [5/6] Démarrage de ngrok...

REM Vérifier si ngrok est disponible
ngrok version >NUL 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Ngrok non installé - Démarrage en mode local uniquement
    goto local_mode
)

REM Démarrer ngrok
start "Ngrok Tunnel - FacebookPost" cmd /c "echo 🌐 Démarrage du tunnel ngrok... && ngrok http 8001 --log=stdout"

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
    echo 💡 Continuez en mode local ou vérifiez ngrok: http://127.0.0.1:4040
    goto local_mode
)

for /f "delims=" %%i in ('curl -s http://127.0.0.1:4040/api/tunnels 2^>NUL') do set "ngrok_response=%%i"
echo %ngrok_response% | findstr "public_url" >NUL 2>&1
if %errorlevel% neq 0 (
    echo ⏳ Tentative %attempts%/10: Tunnel en cours de création...
    timeout /t 3 /nobreak >NUL
    goto get_ngrok_url
)

REM Extraire l'URL (méthode simplifiée Windows)
for /f "tokens=4 delims=:," %%a in ('echo %ngrok_response% ^| findstr "public_url"') do (
    set "ngrok_url=%%a"
)
set "ngrok_url=%ngrok_url:"=%"
set "ngrok_url=%ngrok_url: =%"
if not "%ngrok_url:~0,8%"=="https://" (
    set "ngrok_url=https://%ngrok_url%"
)

if "%ngrok_url%"=="" (
    echo ❌ URL ngrok vide - Mode local activé
    goto local_mode
)

echo ✅ URL ngrok récupérée: %ngrok_url%

echo [6/6] Mise à jour des configurations avec la nouvelle URL...

REM Sauvegarder l'URL ngrok
echo %ngrok_url% > backend\ngrok_url.txt

REM Mettre à jour le frontend .env
cd frontend
if exist ".env" (
    powershell -Command "(Get-Content .env) -replace 'REACT_APP_BACKEND_URL=.*', 'REACT_APP_BACKEND_URL=%ngrok_url%' | Set-Content .env" >NUL 2>&1
    echo ✅ Frontend configuré pour ngrok: %ngrok_url%
)
cd ..

REM Mettre à jour le .env principal
if exist ".env" (
    powershell -Command "(Get-Content .env) -replace 'WEBHOOK_URL=.*', 'WEBHOOK_URL=%ngrok_url%' | Set-Content .env" >NUL 2>&1
    echo ✅ WEBHOOK_URL mis à jour: %ngrok_url%
)

REM Mettre à jour le backend .env
cd backend
if exist ".env" (
    powershell -Command "(Get-Content .env) -replace 'WEBHOOK_URL=.*', 'WEBHOOK_URL=%ngrok_url%' | Set-Content .env" >NUL 2>&1
    echo ✅ Backend WEBHOOK_URL mis à jour: %ngrok_url%
)
cd ..

goto start_frontend

:local_mode
echo.
echo 🏠 MODE LOCAL ACTIVÉ
echo ✅ Backend accessible sur: http://localhost:8001
echo ⚠️ Fonctionnalités limitées (pas de webhooks externes)

:start_frontend
echo.
echo 🚀 Démarrage du frontend React...

REM Démarrer le frontend
start "Frontend React - FacebookPost" cmd /k "cd /d "%~dp0frontend" && echo ⚛️ FacebookPost Frontend && echo 🌐 Interface: http://localhost:3000 && echo 🔗 API Backend: %ngrok_url% && echo. && npm start"

echo ⏳ Initialisation du frontend...
timeout /t 20 /nobreak >NUL

echo.
echo =========================================
echo ✅ APPLICATION DÉMARRÉE AVEC SUCCÈS
echo =========================================
echo.

if not "%ngrok_url%"=="" (
    echo 📋 Services actifs (Mode TUNNEL):
    echo    • Backend API: %ngrok_url%
    echo    • Frontend App: http://localhost:3000
    echo    • Tunnel Ngrok: %ngrok_url%
    echo    • Interface Ngrok: http://127.0.0.1:4040
    echo.
    echo 🎯 Ouverture de l'application...
    start "" "%ngrok_url%"
    echo.
    echo 💡 Instructions:
    echo    • L'application s'ouvre avec l'URL ngrok corrigée
    echo    • Les webhooks Facebook fonctionneront
    echo    • L'URL change à chaque redémarrage de ngrok
) else (
    echo 📋 Services actifs (Mode LOCAL):
    echo    • Backend API: http://localhost:8001
    echo    • Frontend App: http://localhost:3000
    echo.
    echo 🎯 Ouverture de l'application...
    start "" "http://localhost:3000"
    echo.
    echo 💡 Instructions:
    echo    • L'application fonctionne en mode local
    echo    • Pas de webhooks externes (Facebook limité)
    echo    • Pour activer ngrok, installez-le depuis https://ngrok.com
)

echo.
echo 🔧 En cas de problème:
echo    • Vérifiez les fenêtres de commande backend/frontend
echo    • Backend Health: http://localhost:8001/api/health
if not "%ngrok_url%"=="" (
    echo    • Interface Ngrok: http://127.0.0.1:4040
)
echo.
pause
exit /b 0