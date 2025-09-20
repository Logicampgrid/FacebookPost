@echo off
REM ===============================================
REM SCRIPT DE DÉMARRAGE LOCAL - FacebookPost Application
REM Lance backend et frontend en mode local (sans ngrok)
REM ===============================================

echo.
echo =========================================
echo   DÉMARRAGE FACEBOOK POST APPLICATION
echo   MODE LOCAL (Sans tunnel externe)
echo =========================================
echo.

REM Vérifier que nous sommes dans le bon répertoire
if not exist "backend\server.py" (
    echo ❌ Erreur: Fichier server.py non trouvé dans backend\
    echo 💡 Assurez-vous d'exécuter ce script depuis le répertoire racine du projet
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo ❌ Erreur: Fichier package.json non trouvé dans frontend\
    echo 💡 Assurez-vous d'exécuter ce script depuis le répertoire racine du projet
    pause
    exit /b 1
)

echo [1/4] Vérification des prérequis...

REM Vérifier Python
python --version >NUL 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo 💡 Installez Python depuis https://python.org
    pause
    exit /b 1
)
echo ✅ Python détecté

REM Vérifier Node.js/npm
node --version >NUL 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js n'est pas installé ou pas dans le PATH
    echo 💡 Installez Node.js depuis https://nodejs.org
    pause
    exit /b 1
)
echo ✅ Node.js détecté

echo.
echo [2/4] Configuration de l'environnement local...

REM Configuration .env backend pour mode local
echo 🔧 Configuration backend pour mode local...
cd backend
if exist ".env" (
    powershell -Command "(Get-Content .env) -replace 'ENABLE_NGROK=.*', 'ENABLE_NGROK=false' | Set-Content .env" >NUL 2>&1
    echo ✅ Backend configuré en mode local
) else (
    echo ⚠️ Fichier .env backend non trouvé
)
cd ..

REM Configuration .env frontend pour mode local
echo 🔧 Configuration frontend pour mode local...
cd frontend
if exist ".env" (
    powershell -Command "(Get-Content .env) -replace 'REACT_APP_BACKEND_URL=.*', 'REACT_APP_BACKEND_URL=http://localhost:8001' | Set-Content .env" >NUL 2>&1
    echo ✅ Frontend configuré pour backend local
) else (
    echo ⚠️ Fichier .env frontend non trouvé
)
cd ..

REM Mettre à jour le fichier ngrok_url.txt
echo http://localhost:8001 > backend\ngrok_url.txt
echo ✅ URLs cohérentes configurées

echo.
echo [3/4] Installation des dépendances...

REM S'assurer que les dépendances backend sont installées
echo 🔄 Vérification des dépendances Python...
cd backend
pip install -r requirements.txt >NUL 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Erreur lors de l'installation des dépendances Python
    echo 💡 Tentative avec --user...
    pip install --user -r requirements.txt >NUL 2>&1
    if %errorlevel% neq 0 (
        echo ⚠️ Installation des dépendances échouée - continuons quand même
    ) else (
        echo ✅ Dépendances Python installées avec --user
    )
) else (
    echo ✅ Dépendances Python vérifiées
)
cd ..

REM S'assurer que les dépendances frontend sont installées
echo 🔄 Vérification des dépendances Node.js...
cd frontend
if not exist "node_modules" (
    echo 📦 Installation des dépendances Node.js...
    npm install >NUL 2>&1
    if %errorlevel% neq 0 (
        echo ⚠️ Erreur lors de l'installation des dépendances Node.js
    ) else (
        echo ✅ Dépendances Node.js installées
    )
) else (
    echo ✅ Dépendances Node.js disponibles
)
cd ..

REM Créer le build frontend si nécessaire
echo 🔄 Vérification du build frontend...
if not exist "frontend\build\index.html" (
    echo 📦 Build frontend manquant, création en cours...
    cd frontend
    npm run build >NUL 2>&1
    cd ..
    
    if not exist "frontend\build\index.html" (
        echo ⚠️ Erreur lors du build frontend
        echo 💡 Le serveur de développement sera utilisé à la place
    ) else (
        echo ✅ Build frontend créé avec succès
    )
) else (
    echo ✅ Build frontend disponible
)

echo.
echo [4/4] Démarrage des services...

REM Arrêter les processus existants
echo 🛑 Arrêt des processus existants...
taskkill /f /im python.exe /fi "WINDOWTITLE eq *FastAPI*" >NUL 2>&1
taskkill /f /im node.exe /fi "WINDOWTITLE eq *React*" >NUL 2>&1

timeout /t 2 /nobreak >NUL

REM Démarrer le backend FastAPI
echo 🚀 Démarrage du backend FastAPI...
start "Backend FastAPI - FacebookPost (LOCAL)" cmd /k "cd /d "%~dp0backend" && echo 🚀 Serveur FastAPI en mode LOCAL && echo 🌐 API: http://localhost:8001 && echo 🔍 Health: http://localhost:8001/api/health && echo. && python server.py"

REM Attendre que le backend démarre
echo ⏳ Attente du démarrage backend (8 secondes)...
timeout /t 8 /nobreak >NUL

REM Vérifier que le backend répond
echo 🔍 Vérification du backend...
curl -s http://localhost:8001/api/health >NUL 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend actif et fonctionnel
) else (
    echo ⚠️ Backend pas encore prêt (normal si MongoDB démarre)
)

REM Démarrer le frontend React en mode développement
echo ⚛️ Démarrage du frontend React...
start "Frontend React - FacebookPost (LOCAL)" cmd /k "cd /d "%~dp0frontend" && echo ⚛️ Serveur React en mode LOCAL && echo 🌐 Interface: http://localhost:3000 && echo 🔗 Backend: http://localhost:8001 && echo. && npm start"

echo.
echo =========================================
echo ✅ APPLICATION DÉMARRÉE AVEC SUCCÈS
echo =========================================
echo.
echo 📋 Services démarrés en mode LOCAL:
echo    • 🚀 Backend FastAPI : http://localhost:8001 (nouvelle fenêtre)
echo    • ⚛️ Frontend React : http://localhost:3000 (nouvelle fenêtre)
echo    • 💾 MongoDB : Démarré automatiquement
echo.
echo 💡 URLs d'accès:
echo    • 🌐 Application principale: http://localhost:3000
echo    • 🔗 API Backend: http://localhost:8001
echo    • 🩺 Health Check: http://localhost:8001/api/health
echo.
echo 📱 Fonctionnalités disponibles:
echo    • ✅ Publication Facebook (avec tokens configurés)
echo    • ✅ Publication Instagram (avec IDs configurés)
echo    • ✅ Interface utilisateur React complète
echo    • ✅ API Webhook pour N8N: http://localhost:8001/api/webhook
echo    • ✅ OAuth Facebook (avec tokens existants)
echo.
echo ⚠️ MODE LOCAL - Pas d'accès externe:
echo    • L'application n'est accessible QUE depuis cet ordinateur
echo    • Pour un accès externe, utilisez start_complete_application.bat (avec ngrok)
echo    • Les webhooks N8N doivent pointer vers http://localhost:8001
echo.
echo 🎯 L'application va s'ouvrir automatiquement...
timeout /t 5 /nobreak >NUL

REM Ouvrir l'application dans le navigateur
start "" "http://localhost:3000"

echo.
echo ✅ Application ouverte dans le navigateur par défaut
echo 💡 Gardez les fenêtres de commande ouvertes pour que l'application fonctionne
echo.
pause
exit /b 0