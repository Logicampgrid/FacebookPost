@echo off
echo =========================================
echo  DEMARRAGE BACKEND AVEC NGROK - FacebookPost  
echo    Version Windows + Tunnel Internet
echo =========================================
echo.

REM Vérifier que MongoDB tourne
echo 🔍 Vérification de MongoDB...
timeout /t 2 >nul
netstat -an | find "27017" >nul
if errorlevel 1 (
    echo ❌ MongoDB ne semble pas être démarré
    echo.
    echo Veuillez d'abord exécuter 02_start_mongodb.bat
    pause
    exit /b 1
)

echo ✅ MongoDB détecté
echo.

REM Vérifier que ngrok est installé
ngrok version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ngrok n'est pas installé ou pas dans le PATH
    echo.
    echo Veuillez installer ngrok depuis https://ngrok.com/download
    echo Et ajouter ngrok.exe à votre PATH système
    pause
    exit /b 1
)

echo ✅ Ngrok détecté
echo.

REM Configuration avec NGROK activé
set MONGO_URL=mongodb://localhost:27017
set ENABLE_NGROK=true
set DRY_RUN=false
set PUBLICATION_TEST_MODE=true

REM Optionnel: Token d'authentification ngrok pour éviter les limites
REM set NGROK_AUTH_TOKEN=votre_token_ici

echo 🌐 Démarrage avec tunnel ngrok (accès internet)...
echo 📱 L'application sera accessible depuis n'importe où sur internet
echo 🔐 Mode test activé pour économiser les crédits
echo.
echo ⚠️  IMPORTANT: Laissez cette fenêtre ouverte pendant l'utilisation
echo 🌐 Le navigateur s'ouvrira automatiquement avec l'URL ngrok
echo.

REM Changer vers le répertoire backend
cd /d "%~dp0..\backend"

REM Démarrer le serveur avec ngrok
python server_windows.py

REM Si on arrive ici, le backend s'est arrêté
echo.
echo ℹ️  Le serveur backend et ngrok se sont arrêtés
pause