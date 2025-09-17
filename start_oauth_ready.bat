@echo off
echo.
echo =========================================
echo  FACEBOOK OAUTH - CONFIGURATION AUTOMATIQUE
echo =========================================
echo.

:: Étape 1: Démarrer ngrok
echo [1/4] Démarrage du tunnel ngrok...
call "%~dp099_start_all_ngrok.bat"
if %errorlevel% neq 0 (
    echo ❌ Erreur lors du démarrage de ngrok
    pause
    exit /b 1
)

:: Étape 2: Synchroniser les configurations
echo.
echo [2/4] Synchronisation des configurations OAuth...
python "%~dp0sync_ngrok_config.py"
if %errorlevel% neq 0 (
    echo ⚠️ Problème de synchronisation, mais on continue...
)

:: Étape 3: Démarrer le serveur backend
echo.
echo [3/4] Démarrage du serveur backend...
start "Backend OAuth Ready" cmd /c "python %~dp0server_windows.py"

:: Attendre que le backend démarre
echo ⏳ Attente du démarrage du backend...
timeout /t 5 /nobreak >NUL

:: Étape 4: Vérification finale
echo.
echo [4/4] Vérification de la configuration OAuth...
python "%~dp0check_oauth_config.py"

echo.
echo =========================================
echo ✅ SYSTÈME OAUTH FACEBOOK PRÊT !
echo =========================================
echo.
echo 💡 Prochaines étapes:
echo 1. Consultez le fichier 'oauth_config_summary.txt' pour les URLs à configurer
echo 2. Mettez à jour votre application Facebook Developer avec ces URLs
echo 3. Testez l'authentification sur votre application
echo.
echo 🌐 Gardez toutes les fenêtres ouvertes pendant les tests
echo.
pause