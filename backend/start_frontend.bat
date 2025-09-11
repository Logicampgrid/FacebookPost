@echo off
REM ===============================================
REM Script de démarrage Frontend FacebookPost
REM ===============================================

echo.
echo ====================================
echo   Facebook Post - Frontend React
echo ====================================
echo.

cd /d "C:\FacebookPost\frontend"

REM Vérifier que Node.js est installé
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR: Node.js non trouve dans le PATH
    echo 💡 Installez Node.js depuis https://nodejs.org
    pause
    exit /b 1
)

REM Vérifier que npm est disponible
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR: npm non trouve
    echo 💡 Réinstallez Node.js
    pause
    exit /b 1
)

REM Installer les dépendances si nécessaire
if not exist "node_modules\" (
    echo 📦 Installation dépendances npm...
    npm install
)

REM Vérifier le fichier .env
if not exist ".env" (
    echo 📝 Création fichier .env frontend...
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > .env
    echo GENERATE_SOURCEMAP=false >> .env
)

REM Construire le projet
echo 🔨 Construction du projet React...
npm run build

if errorlevel 1 (
    echo ❌ ERREUR: Échec de la construction
    echo 💡 Vérifiez les erreurs ci-dessus
    pause
    exit /b 1
)

echo.
echo ✅ Construction terminée
echo 🚀 Démarrage serveur de développement...
echo 🌐 URL: http://localhost:3000
echo.
echo Pour arrêter: Ctrl+C
echo.

npm start

pause