@echo off
echo.
echo ========================================
echo  NGROK TUNNEL STARTUP - OAuth Ready
echo ========================================
echo.

:: Vérifier si ngrok est installé
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ngrok n'est pas installé ou pas dans le PATH
    echo.
    echo 💡 Pour installer ngrok:
    echo 1. Allez sur https://ngrok.com/download
    echo 2. Téléchargez et installez ngrok
    echo 3. Ajoutez ngrok au PATH système
    echo.
    pause
    exit /b 1
)

:: Arrêter les processus ngrok existants
echo [1/4] Arrêt des processus ngrok existants...
tasklist /FI "IMAGENAME eq ngrok.exe" 2>NUL | find /I /N "ngrok.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo ⚠️ Arrêt des processus ngrok existants...
    taskkill /f /im ngrok.exe >NUL 2>&1
    timeout /t 2 /nobreak >NUL
)

:: Démarrer ngrok
echo.
echo [2/4] Démarrage du tunnel ngrok...
echo 🚀 Lancement de ngrok sur le port 8001...
start "Ngrok Tunnel" cmd /c "ngrok http 8001 --log=stdout"

:: Attendre que ngrok démarre
echo.
echo [3/4] Attente de l'initialisation du tunnel...
echo ⏳ Patientez pendant que ngrok se connecte...

:: Boucle d'attente pour récupérer l'URL ngrok
set "ngrok_url="
set /a attempts=0
set /a max_attempts=30

:wait_ngrok
set /a attempts+=1
if %attempts% gtr %max_attempts% (
    echo ❌ Timeout: Impossible de récupérer l'URL ngrok après %max_attempts% tentatives
    echo 💡 Vérifiez votre connexion internet et votre configuration ngrok
    pause
    exit /b 1
)

:: Attendre 2 secondes entre chaque tentative
timeout /t 2 /nobreak >NUL

:: Essayer de récupérer l'URL ngrok via l'API
for /f "delims=" %%i in ('curl -s http://127.0.0.1:4040/api/tunnels 2^>NUL') do set "ngrok_response=%%i"

:: Vérifier si la réponse contient une URL
echo %ngrok_response% | findstr "public_url" >NUL 2>&1
if %errorlevel% neq 0 (
    echo ⏳ Tentative %attempts%/%max_attempts%: Tunnel en cours de création...
    goto wait_ngrok
)

:: Extraire l'URL ngrok (méthode simple pour Windows)
for /f "tokens=2 delims=:" %%a in ('echo %ngrok_response% ^| findstr "public_url"') do (
    for /f "tokens=1 delims=," %%b in ("%%a") do (
        set "ngrok_url=%%b"
    )
)

:: Nettoyer l'URL (enlever les guillemets et espaces)
set "ngrok_url=%ngrok_url:"=%"
set "ngrok_url=%ngrok_url: =%"

:: Vérifier si l'URL est valide
if "%ngrok_url%"=="" (
    echo ⏳ Tentative %attempts%/%max_attempts%: URL non encore disponible...
    goto wait_ngrok
)

:: Ajouter https:// si manquant et nettoyer
if not "%ngrok_url:~0,8%"=="https://" (
    if not "%ngrok_url:~0,7%"=="http://" (
        set "ngrok_url=https://%ngrok_url%"
    )
)

echo.
echo [4/5] Configuration des URLs OAuth...
echo ✅ URL Ngrok récupérée: %ngrok_url%

:: Sauvegarder l'URL dans un fichier pour le backend
echo %ngrok_url% > "%~dp0backend\ngrok_url.txt"

:: Mettre à jour le fichier .env du frontend
python "%~dp0update_frontend_env.py" "%ngrok_url%" 2>NUL
if %errorlevel% neq 0 (
    echo ⚠️ Script Python non disponible, mise à jour manuelle du frontend .env...
    call :update_frontend_env "%ngrok_url%"
)

echo.
echo [5/5] Mise à jour automatique Facebook OAuth...
echo 🔄 Configuration des domaines Facebook avec l'URL ngrok...

:: Lancer la mise à jour Facebook en arrière-plan
start /MIN cmd /c ""%~dp0update_facebook_config.bat" && echo ✅ Facebook OAuth configuré avec succès!"

echo.
echo ========================================
echo ✅ NGROK TUNNEL CONFIGURÉ AVEC SUCCÈS
echo ========================================
echo.
echo 🌐 URL Publique: %ngrok_url%
echo 📱 Accessible depuis n'importe où sur Internet
echo 🔐 OAuth Facebook configuré automatiquement
echo.
echo 💡 URLs importantes:
echo    • Application: %ngrok_url%
echo    • API Backend: %ngrok_url%/api/health
echo    • Interface Ngrok: http://127.0.0.1:4040
echo.
echo ⚠️ IMPORTANT:
echo    • Gardez cette fenêtre ouverte
echo    • L'URL ngrok change à chaque redémarrage
echo    • Les configurations sont mises à jour automatiquement
echo.
echo Appuyez sur une touche pour continuer...
pause >NUL
exit /b 0

:update_frontend_env
:: Fonction pour mettre à jour le .env du frontend
set "new_url=%~1"
set "env_file=%~dp0frontend\.env"

if not exist "%env_file%" (
    echo ⚠️ Fichier .env frontend non trouvé: %env_file%
    exit /b 1
)

:: Créer une copie de sauvegarde
copy "%env_file%" "%env_file%.backup" >NUL 2>&1

:: Créer un fichier temporaire avec les nouvelles valeurs
set "temp_file=%env_file%.tmp"
> "%temp_file%" (
    for /f "usebackq delims=" %%a in ("%env_file%") do (
        set "line=%%a"
        call :process_line
    )
)

:: Remplacer l'ancien fichier
move "%temp_file%" "%env_file%" >NUL 2>&1
echo ✅ Frontend .env mis à jour avec: %new_url%
exit /b 0

:process_line
if "%line:~0,21%"=="REACT_APP_BACKEND_URL" (
    echo REACT_APP_BACKEND_URL=%new_url%
) else (
    echo %line%
)
exit /b 0