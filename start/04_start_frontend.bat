@echo off
echo =========================================
echo   DEMARRAGE FRONTEND - FacebookPost
echo =========================================
echo.

REM Vérifier que le backend tourne
echo 🔍 Vérification du backend...
timeout /t 2 >nul
netstat -an | find "8001" >nul
if errorlevel 1 (
    echo ❌ Le backend ne semble pas être démarré
    echo.
    echo Veuillez d'abord exécuter 03_start_backend.bat
    pause
    exit /b 1
)

echo ✅ Backend détecté
echo.

REM Configurer les variables d'environnement pour le frontend
set REACT_APP_BACKEND_URL=http://localhost:8001
set DANGEROUSLY_DISABLE_HOST_CHECK=true
set HOST=localhost
set PORT=3000

REM Démarrer le frontend
echo 🚀 Démarrage du frontend sur http://localhost:3000...
echo.
echo ⚠️  IMPORTANT: Laissez cette fenêtre ouverte pendant l'utilisation de l'application
echo 🌐 L'application s'ouvrira automatiquement dans votre navigateur
echo.

cd /d "%~dp0..\frontend"

REM Construire le frontend pour production (plus rapide)
echo 📦 Construction du frontend...
npm run build
if errorlevel 1 (
    echo ❌ Erreur lors de la construction du frontend
    echo Tentative de démarrage en mode développement...
    npm start
) else (
    echo ✅ Frontend construit avec succès
    echo 🌐 Application disponible via le backend à http://localhost:8001
    echo.
    echo Le frontend a été intégré dans le backend.
    echo Vous pouvez fermer cette fenêtre et accéder à l'application via http://localhost:8001
)

pause