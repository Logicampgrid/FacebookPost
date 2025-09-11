@echo off
REM ===============================================
REM Script de démarrage Backend FacebookPost
REM ===============================================

echo.
echo ====================================
echo   Facebook Post - Backend Windows
echo ====================================
echo.

cd /d "C:\FacebookPost\backend"

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR: Python non trouve dans le PATH
    echo 💡 Installez Python depuis https://python.org
    pause
    exit /b 1
)

REM Vérifier que MongoDB est démarré
echo 🔍 Vérification MongoDB...
"C:\Program Files\MongoDB\Server\8.0\bin\mongosh.exe" --eval "db.runCommand('ping')" --quiet >nul 2>&1
if errorlevel 1 (
    echo ⚠️  MongoDB non accessible, démarrage...
    echo 🚀 Lancement MongoDB...
    start "" "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --dbpath "C:\FacebookPost\data\db"
    timeout /t 5 /nobreak >nul
)

REM Installer les dépendances si nécessaire
if not exist "venv\" (
    echo 📦 Création environnement virtuel...
    python -m venv venv
)

echo 🔧 Activation environnement virtuel...
call venv\Scripts\activate.bat

echo 📚 Installation dépendances...
pip install -r requirements.txt

REM Vérifier le fichier .env
if not exist ".env" (
    echo 📝 Création fichier .env...
    echo MONGO_URL=mongodb://localhost:27017 > .env
    echo FACEBOOK_APP_ID=your_app_id >> .env
    echo FACEBOOK_APP_SECRET=your_app_secret >> .env
    echo ENABLE_NGROK=false >> .env
    echo DRY_RUN=true >> .env
    echo PUBLICATION_TEST_MODE=true >> .env
)

echo.
echo ✅ Configuration terminée
echo 🚀 Démarrage serveur FastAPI...
echo 🌐 URL: http://localhost:8001
echo.
echo Pour arrêter: Ctrl+C
echo.

python server_windows.py

pause