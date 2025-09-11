@echo off
echo =========================================
echo    DEMARRAGE BACKEND - FacebookPost
echo    Version Windows Optimisée
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

REM Définir les variables d'environnement pour usage local
set MONGO_URL=mongodb://localhost:27017
set ENABLE_NGROK=false
set PUBLIC_BASE_URL=http://localhost:8001
set REACT_APP_BACKEND_URL=http://localhost:8001
set DRY_RUN=false
set PUBLICATION_TEST_MODE=true

REM Créer répertoires nécessaires
if not exist "C:\FacebookPost\logs" (
    mkdir "C:\FacebookPost\logs"
)

echo 🚀 Démarrage du serveur backend Windows sur http://localhost:8001...
echo.
echo ⚠️  IMPORTANT: Laissez cette fenêtre ouverte pendant l'utilisation de l'application
echo 📁 Répertoires Windows : C:\FacebookPost\
echo 💾 Logs disponibles dans : C:\FacebookPost\logs\
echo.

REM Changer vers le répertoire backend
cd /d "%~dp0..\backend"

REM Démarrer le serveur Windows optimisé
python server_windows.py

REM Si on arrive ici, le backend s'est arrêté
echo.
echo ℹ️  Le serveur backend s'est arrêté
pause