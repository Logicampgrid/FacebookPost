@echo off
echo =========================================
echo   DEMARRAGE COMPLET - FacebookPost
echo     Version Windows Optimisée  
echo =========================================
echo.

echo 🚀 Démarrage automatique de tous les services Windows...
echo.

REM Créer les répertoires nécessaires
echo 📁 Création des répertoires...
if not exist "C:\FacebookPost\data" (
    mkdir "C:\FacebookPost\data"
    echo   ✅ Répertoire data créé
)

if not exist "C:\FacebookPost\logs" (
    mkdir "C:\FacebookPost\logs"
    echo   ✅ Répertoire logs créé
)

if not exist "C:\FacebookPost\backend\uploads" (
    mkdir "C:\FacebookPost\backend\uploads"
    echo   ✅ Répertoire uploads créé
)

echo.
echo 1/3 - Démarrage de MongoDB en arrière-plan...
start /min "MongoDB-FacebookPost" cmd /c "%~dp0\02_start_mongodb.bat"

echo ⏳ Attente du démarrage de MongoDB (8 secondes)...
timeout /t 8 >nul

REM Vérifier que MongoDB est vraiment démarré
netstat -an | find "27017" >nul
if errorlevel 1 (
    echo ❌ MongoDB n'a pas pu démarrer correctement
    echo.
    echo Veuillez vérifier que MongoDB est installé et configuré
    pause
    exit /b 1
)

echo ✅ MongoDB opérationnel
echo.

echo 2/3 - Construction du frontend React...
cd /d "%~dp0..\frontend"

REM Configuration locale pour le build
set REACT_APP_BACKEND_URL=http://localhost:8001
set GENERATE_SOURCEMAP=false

REM Build optimisé du frontend
call npm run build >nul 2>&1
if errorlevel 1 (
    echo ❌ Erreur lors de la construction du frontend
    echo Vérifiez que Node.js et npm sont installés
    echo.
    pause
    exit /b 1
)

echo ✅ Frontend construit avec succès
echo.

echo 3/3 - Démarrage du serveur backend Windows...
start "Backend-FacebookPost" cmd /k "%~dp0\03_start_backend.bat"

echo ⏳ Attente du démarrage du backend (5 secondes)...
timeout /t 5 >nul

echo.
echo 🎉 TOUS LES SERVICES SONT DÉMARRÉS !
echo.
echo 🌐 Application accessible à : http://localhost:8001
echo.

REM Ouvrir l'application dans le navigateur par défaut
start http://localhost:8001

echo 📋 Services Windows actifs :
echo   - MongoDB        : Port 27017 (fenêtre minimisée)
echo   - Backend API    : Port 8001 (fenêtre ouverte)
echo   - Frontend React : Intégré dans le backend
echo.
echo 💾 Logs disponibles dans : C:\FacebookPost\logs\
echo 📁 Données stockées dans : C:\FacebookPost\data\
echo.
echo ⚠️  Pour arrêter l'application :
echo     - Fermez les fenêtres de commande ouvertes
echo     - Ou exécutez stop_all.bat
echo.

echo 🎯 Prochaines étapes :
echo   1. Connecter votre Business Manager Facebook
echo   2. Sélectionner vos pages/groupes/Instagram
echo   3. Créer votre première publication
echo.

pause