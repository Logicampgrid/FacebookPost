@echo off
REM ===============================================
REM SCRIPT DE DÉMARRAGE COMPLET - FacebookPost Application
REM Lance ngrok, backend et frontend dans des fenêtres séparées
REM ===============================================

echo.
echo =========================================
echo   DÉMARRAGE FACEBOOK POST APPLICATION
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

REM Vérifier ngrok
ngrok version >NUL 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ngrok n'est pas installé ou pas dans le PATH
    echo 💡 Installez ngrok depuis https://ngrok.com/download
    pause
    exit /b 1
)
echo ✅ Ngrok détecté

echo.
echo [2/4] Préparation de l'environnement...

REM S'assurer que les dépendances backend sont installées
echo 🔄 Vérification des dépendances Python...
cd backend
pip install -r requirements.txt >NUL 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Erreur lors de l'installation des dépendances Python
    echo 💡 Vérifiez requirements.txt et votre environnement Python
)
cd ..

REM S'assurer que le frontend est buildé
echo 🔄 Vérification du build frontend...
if not exist "frontend\build\index.html" (
    echo 📦 Build frontend manquant, création en cours...
    cd frontend
    npm install >NUL 2>&1
    npm run build >NUL 2>&1
    cd ..
    
    if not exist "frontend\build\index.html" (
        echo ⚠️ Erreur lors du build frontend
        echo 💡 Exécutez manuellement 'npm run build' dans le dossier frontend
    ) else (
        echo ✅ Build frontend créé avec succès
    )
) else (
    echo ✅ Build frontend disponible
)

echo.
echo [3/4] Démarrage des services...

REM Arrêter les processus existants
echo 🛑 Arrêt des processus existants...
taskkill /f /im python.exe /fi "WINDOWTITLE eq *FastAPI*" >NUL 2>&1
taskkill /f /im node.exe /fi "WINDOWTITLE eq *React*" >NUL 2>&1
taskkill /f /im ngrok.exe >NUL 2>&1

timeout /t 2 /nobreak >NUL

REM Démarrer ngrok et configurer Facebook OAuth
echo 🌐 Démarrage du tunnel ngrok...
start "Configuration Ngrok et Facebook OAuth" cmd /c ""%~dp099_start_all_ngrok.bat" && echo 🎯 Configuration terminée - Vous pouvez fermer cette fenêtre && pause"

REM Attendre que ngrok soit configuré
echo ⏳ Attente de la configuration ngrok (15 secondes)...
timeout /t 15 /nobreak >NUL

REM Démarrer le backend FastAPI
echo 🚀 Démarrage du backend FastAPI...
start "Backend FastAPI - FacebookPost" cmd /k "cd /d "%~dp0backend" && echo 🚀 Démarrage du serveur FastAPI... && python server.py"

REM Attendre que le backend démarre
echo ⏳ Attente du démarrage backend (10 secondes)...
timeout /t 10 /nobreak >NUL

REM Démarrer le frontend React (développement)
echo ⚛️ Démarrage du frontend React...
start "Frontend React - FacebookPost" cmd /k "cd /d "%~dp0frontend" && echo ⚛️ Démarrage du serveur React... && npm start"

echo.
echo [4/4] Vérification et ouverture...

REM Attendre que tous les services soient prêts
echo ⏳ Finalisation du démarrage (20 secondes)...
timeout /t 20 /nobreak >NUL

REM Tenter de récupérer l'URL ngrok pour l'ouverture
setlocal enabledelayedexpansion
set "ngrok_url="
for /f "delims=" %%i in ('curl -s http://127.0.0.1:4040/api/tunnels 2^>NUL') do set "ngrok_response=%%i"

echo !ngrok_response! | findstr "public_url" >NUL 2>&1
if !errorlevel! equ 0 (
    REM Extraire l'URL ngrok
    for /f "tokens=4 delims=:," %%a in ('echo !ngrok_response! ^| findstr "public_url"') do (
        set "raw_url=%%a"
    )
    set "ngrok_url=!raw_url:"=!"
    set "ngrok_url=!ngrok_url: =!"
    
    if not "!ngrok_url:~0,8!"=="https://" (
        if not "!ngrok_url:~0,7!"=="http://" (
            set "ngrok_url=https://!ngrok_url!"
        )
    )
    
    echo 🌐 Ouverture de l'application: !ngrok_url!
    start "" "!ngrok_url!"
) else (
    echo ⚠️ URL ngrok non détectée, ouverture sur localhost
    start "" "http://localhost:8001"
)

echo.
echo =========================================
echo ✅ APPLICATION DÉMARRÉE AVEC SUCCÈS
echo =========================================
echo.
echo 📋 Services démarrés:
echo    • 🌐 Ngrok Tunnel : Actif (nouvelle fenêtre)
echo    • 🚀 Backend FastAPI : http://localhost:8001 (nouvelle fenêtre)
echo    • ⚛️ Frontend React : http://localhost:3000 (nouvelle fenêtre)
echo    • 🔐 Facebook OAuth : Configuré automatiquement
echo.
echo 💡 URLs importantes:
if defined ngrok_url (
    echo    • Application publique: %ngrok_url%
) else (
    echo    • Application locale: http://localhost:8001
)
echo    • Interface Ngrok: http://127.0.0.1:4040
echo    • React Dev Server: http://localhost:3000
echo.
echo ⚠️ IMPORTANT:
echo    • Gardez toutes les fenêtres ouvertes
echo    • L'URL ngrok change à chaque redémarrage
echo    • Facebook OAuth est automatiquement mis à jour
echo.
echo 🎯 L'application devrait s'ouvrir automatiquement dans votre navigateur
echo.
pause
exit /b 0