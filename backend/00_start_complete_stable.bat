@echo off
chcp 65001 >nul
title DÉMARRAGE COMPLET FACEBOOK POST - URL STABLE
color 0E

echo.
echo =============================================
echo   FACEBOOK POST - DÉMARRAGE URL STABLE
echo =============================================
echo.
echo 🎯 Cette nouvelle approche résout le problème d'URL changeante
echo 📌 Ngrok démarrera dans une fenêtre séparée avec URL stable
echo 🔄 Le serveur détectera l'URL ngrok existante
echo.
echo 💡 AVANTAGES:
echo    - URL ngrok stable (ne change plus)
echo    - Configuration Facebook à faire UNE FOIS seulement
echo    - Redémarrages serveur sans impact sur ngrok
echo.

cd /d "%~dp0"

set /p confirm="🚀 Démarrer avec la nouvelle approche stable? (O/n): "
if /i "%confirm%"=="n" (
    echo Annulé par l'utilisateur
    pause
    exit /b 0
)

echo.
echo ===== ÉTAPE 1/2: DÉMARRAGE NGROK =====
echo.
echo 🌐 Démarrage ngrok dans une fenêtre séparée...
echo 💡 Cette fenêtre va s'ouvrir et doit rester ouverte

:: Démarrer ngrok dans une nouvelle fenêtre
start "NGROK STABLE" cmd /c "01_start_ngrok_only.bat"

echo.
echo ⏳ Attente du démarrage ngrok (15 secondes)...
timeout /t 15 /nobreak >nul

echo.
echo 🔍 Vérification que ngrok est actif...
curl -s http://127.0.0.1:4040/api/tunnels >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ Ngrok ne répond pas encore
    echo ⏳ Attente supplémentaire (10 secondes)...
    timeout /t 10 /nobreak >nul
    
    curl -s http://127.0.0.1:4040/api/tunnels >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo ❌ ERREUR: Ngrok ne démarre pas correctement
        echo 💡 Vérifiez la fenêtre ngrok pour les erreurs
        echo 💡 Appuyez sur une touche pour continuer quand même...
        pause >nul
    ) else (
        echo ✅ Ngrok est maintenant actif
    )
) else (
    echo ✅ Ngrok est actif
)

echo.
echo ===== ÉTAPE 2/2: DÉMARRAGE SERVEUR =====
echo.
echo 🔄 Le serveur va détecter automatiquement l'URL ngrok
echo 📋 Configuration Facebook sera affichée au démarrage
echo.

:: Démarrer le serveur backend
echo 🚀 Démarrage du serveur backend...
echo.
python server.py

echo.
echo 🛑 Session terminée
echo.
echo 💡 IMPORTANT: 
echo    - La fenêtre ngrok doit rester ouverte
echo    - Fermez-la seulement quand vous avez terminé
echo.
pause