@echo off
chcp 65001 >nul
title SERVEUR BACKEND - DÉTECTION NGROK
color 0B

echo.
echo =====================================
echo   SERVEUR BACKEND - DÉTECTION NGROK  
echo =====================================
echo.
echo 🎯 Ce script démarre seulement le serveur backend
echo 🔍 Il détecte automatiquement l'URL ngrok existante
echo 💡 Démarrez d'abord ngrok avec 01_start_ngrok_only.bat
echo.

cd /d "%~dp0"

:: Vérifier si ngrok est actif
echo 🔍 Vérification de ngrok...
curl -s http://127.0.0.1:4040/api/tunnels >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  ATTENTION: Ngrok ne semble pas être actif
    echo 💡 Démarrez d'abord ngrok avec: 01_start_ngrok_only.bat
    echo.
    set /p continue="Continuer quand même? (o/N): "
    if /i not "%continue%"=="o" (
        echo Annulé par l'utilisateur
        pause
        exit /b 1
    )
) else (
    echo ✅ Ngrok détecté et actif
)

echo.
echo 🚀 Démarrage du serveur backend...
echo 📋 Mode: Détection ngrok existant
echo.

:: Démarrer le serveur Python
python server.py

echo.
echo 🛑 Serveur arrêté
pause