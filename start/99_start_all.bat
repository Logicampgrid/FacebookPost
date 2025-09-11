@echo off
echo =========================================
echo   DEMARRAGE COMPLET - FacebookPost
echo =========================================
echo.

echo 🚀 Démarrage automatique de tous les services...
echo.

REM Créer le répertoire data s'il n'existe pas
if not exist "%~dp0..\data" (
    echo 📁 Création du répertoire data...
    mkdir "%~dp0..\data"
)

echo 1/3 - Démarrage de MongoDB en arrière-plan...
start /min cmd /c "%~dp0\02_start_mongodb.bat"

echo ⏳ Attente du démarrage de MongoDB (5 secondes)...
timeout /t 5 >nul

echo 2/3 - Démarrage du backend en arrière-plan...
start /min cmd /c "%~dp0\03_start_backend.bat"

echo ⏳ Attente du démarrage du backend (3 secondes)...
timeout /t 3 >nul

echo 3/3 - Construction du frontend...
cd /d "%~dp0..\frontend"
set REACT_APP_BACKEND_URL=http://localhost:8001
npm run build >nul 2>&1

echo.
echo ✅ Tous les services sont démarrés !
echo.
echo 🌐 Application accessible à : http://localhost:8001
echo.

REM Ouvrir l'application dans le navigateur
start http://localhost:8001

echo 📋 Services démarrés :
echo   - MongoDB : Port 27017
echo   - Backend : Port 8001 
echo   - Frontend : Intégré dans le backend
echo.
echo ⚠️  Pour arrêter l'application, fermez toutes les fenêtres de commande
echo     ou exécutez stop_all.bat
echo.

pause