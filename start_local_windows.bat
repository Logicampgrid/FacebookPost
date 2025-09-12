@echo off
echo.
echo ============================================
echo  TUNNEL INSTAGRAM GRATUIT - Windows Local
echo ============================================
echo.

:: Vérifier si MongoDB est démarré
echo [1/5] Verification MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ MongoDB est déjà en cours d'exécution
) else (
    echo ⚠️ MongoDB n'est pas démarré. Démarrage...
    net start MongoDB 2>NUL
    if errorlevel 1 (
        echo ❌ Impossible de démarrer MongoDB automatiquement
        echo 💡 Démarrez MongoDB manuellement puis relancez ce script
        pause
        exit /b 1
    )
)

:: Aller dans le répertoire backend
echo.
echo [2/5] Démarrage du backend FastAPI...
cd /d "%~dp0backend"

:: Installer les dépendances Python si nécessaire
if not exist venv (
    echo 📦 Création de l'environnement virtuel Python...
    python -m venv venv
)

:: Activer l'environnement virtuel
call venv\Scripts\activate.bat

:: Installer les dépendances
pip install -r requirements.txt >NUL 2>&1

:: Démarrer le backend en arrière-plan
echo 🚀 Lancement du serveur backend (port 8001)...
start "Backend FastAPI" cmd /c "python server.py"

:: Attendre que le backend démarre
echo ⏳ Attente du démarrage du backend...
:wait_backend
timeout /t 2 /nobreak >NUL
curl -s http://localhost:8001/api/health >NUL 2>&1
if errorlevel 1 (
    echo ⏳ Backend en cours de démarrage...
    goto wait_backend
)
echo ✅ Backend démarré avec succès !

:: Aller dans le répertoire frontend
echo.
echo [3/5] Préparation du frontend React...
cd /d "%~dp0frontend"

:: Installer les dépendances Node.js si nécessaire
if not exist node_modules (
    echo 📦 Installation des dépendances React...
    npm install
)

:: Construire le frontend
echo 🔨 Construction du frontend...
npm run build >NUL 2>&1

echo.
echo [4/5] Démarrage de ngrok (tunnel public)...
cd /d "%~dp0"

:: Lancer ngrok si le fichier existe
if exist "99_start_all_ngrok.bat" (
    echo 🌐 Lancement de votre tunnel ngrok...
    start "Ngrok Tunnel" cmd /c "99_start_all_ngrok.bat"
) else (
    echo 🌐 Lancement ngrok standard...
    start "Ngrok Tunnel" cmd /c "ngrok http 8001"
)

:: Attendre que ngrok démarre et récupérer l'URL
echo ⏳ Attente de l'initialisation du tunnel ngrok...
timeout /t 10 /nobreak >NUL

:: Essayer de récupérer l'URL ngrok
for /f "tokens=*" %%i in ('curl -s http://127.0.0.1:4040/api/tunnels 2^>NUL ^| findstr "public_url"') do (
    set ngrok_response=%%i
)

echo.
echo [5/5] Application prête !
echo ============================================
echo.
echo 🎉 TUNNEL INSTAGRAM GRATUIT - ACTIF
echo.
echo 📍 URLs d'accès :
echo    • Backend local : http://localhost:8001
echo    • Frontend local: http://localhost:3000  
echo    • API Health    : http://localhost:8001/api/health
echo.
echo 🌐 URL Publique Ngrok :
echo    Consultez la fenêtre ngrok ou http://127.0.0.1:4040
echo.
echo 🚀 L'application est prête pour les tests !
echo.
echo ============================================
echo.
echo 💡 Instructions :
echo 1. Ouvrez http://localhost:3000 dans votre navigateur
echo 2. Utilisez "Token manuel" pour vous connecter
echo 3. L'URL ngrok sera utilisée pour les webhooks externes
echo.
echo Appuyez sur une touche pour ouvrir l'application...
pause >NUL

:: Ouvrir l'application dans le navigateur
start http://localhost:3000

echo.
echo ✅ Application lancée ! 
echo.
echo Pour arrêter l'application :
echo - Fermez cette fenêtre
echo - Fermez les fenêtres "Backend FastAPI" et "Ngrok Tunnel"
echo.
pause