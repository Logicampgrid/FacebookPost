@echo off
chcp 65001 >nul
title NGROK STANDALONE - URL STABLE
color 0A

echo.
echo =====================================
echo      NGROK STANDALONE - URL STABLE
echo =====================================
echo.
echo 🎯 Ce script démarre ngrok de manière indépendante
echo 📌 L'URL restera stable même si le serveur redémarre
echo 💡 Laissez cette fenêtre ouverte pendant l'utilisation
echo.

:: Aller dans le dossier start
cd /d "%~dp0"

:: Vérifier si Python est disponible
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python non trouvé dans le PATH
    echo 💡 Assurez-vous que Python est installé et accessible
    pause
    exit /b 1
)

:: Vérifier si le script existe
if not exist "start_ngrok_standalone.py" (
    echo ❌ Script start_ngrok_standalone.py non trouvé
    echo 💡 Assurez-vous d'être dans le bon répertoire
    pause
    exit /b 1
)

echo 🚀 Démarrage ngrok standalone...
echo.

:: Démarrer ngrok avec surveillance optionnelle
echo 💡 Choisissez le mode:
echo    [1] Mode normal (nécessite cette fenêtre ouverte)
echo    [2] Mode surveillance (redémarre automatiquement si ngrok plante)
echo.
set /p choice="Votre choix (1 ou 2): "

if "%choice%"=="2" (
    echo.
    echo 🔍 Mode surveillance activé
    python start_ngrok_standalone.py --monitor
) else (
    echo.
    echo 📌 Mode normal activé
    python start_ngrok_standalone.py
)

echo.
echo 🛑 Ngrok arrêté
pause