@echo off
echo =========================================
echo  DEMARRAGE COMPLET AVEC NGROK - FacebookPost
echo    Accès Internet + Tunnel Public
echo =========================================
echo.

REM Vérifier ngrok
ngrok version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ngrok n'est pas installé
    echo.
    echo 💡 Installation rapide :
    echo   1. Téléchargez depuis https://ngrok.com/download
    echo   2. Décompressez ngrok.exe dans C:\Windows\System32\
    echo   3. Redémarrez cette application
    echo.
    pause
    exit /b 1
)

echo ✅ Ngrok détecté
echo.

echo 🌐 DÉMARRAGE AVEC TUNNEL INTERNET NGROK
echo.
echo 📡 Votre application sera accessible depuis n'importe où !
echo 🔐 URL sécurisée générée automatiquement
echo 💰 Mode test activé (économise les crédits)
echo.

echo 🚀 Démarrage des services...
echo.

REM Créer les répertoires nécessaires
if not exist "C:\FacebookPost\data" mkdir "C:\FacebookPost\data"
if not exist "C:\FacebookPost\logs" mkdir "C:\FacebookPost\logs"
if not exist "C:\FacebookPost\backend\uploads" mkdir "C:\FacebookPost\backend\uploads"

echo 1/4 - MongoDB en arrière-plan...
start /min "MongoDB-FacebookPost" cmd /c "%~dp0\02_start_mongodb.bat"
timeout /t 8 >nul

echo 2/4 - Construction du frontend...
cd /d "%~dp0..\frontend"
set REACT_APP_BACKEND_URL=http://localhost:8001
call npm run build >nul 2>&1

echo 3/4 - Démarrage du backend avec ngrok...
echo.
echo ⏳ Génération de l'URL publique ngrok...
echo    (Cela peut prendre jusqu'à 60 secondes)
echo.
start "Backend-FacebookPost-Ngrok" cmd /k "%~dp0\03_start_backend_ngrok.bat"

echo 4/4 - Finalisation...
timeout /t 10 >nul

echo.
echo 🎉 APPLICATION ACCESSIBLE SUR INTERNET !
echo.
echo 🌐 L'URL ngrok sera affichée dans la fenêtre du backend
echo 🌐 Le navigateur s'ouvrira automatiquement
echo.
echo 📋 Services actifs :
echo   - MongoDB : Port 27017 (local)
echo   - Backend : Port 8001 (local + ngrok)
echo   - Ngrok   : URL publique générée
echo.
echo 💡 Partage possible :
echo   - Envoyez l'URL ngrok à vos collaborateurs
echo   - Configurez des webhooks avec cette URL
echo   - Testez depuis votre mobile
echo.
echo ⚠️  Sécurité :
echo   - URL temporaire (change à chaque démarrage)
echo   - Accès public (protégez vos données sensibles)
echo.

pause