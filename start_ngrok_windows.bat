@echo off
REM ===============================================
REM SCRIPT DE DÉMARRAGE NGROK AUTOMATIQUE
REM Résout le problème de page blanche ngrok
REM ===============================================

echo.
echo =========================================
echo   🚀 DÉMARRAGE NGROK - FACEBOOKPOST
echo =========================================
echo.

REM Vérifier Python
python --version >NUL 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python requis mais non trouvé
    echo 💡 Installez Python depuis https://python.org
    pause
    exit /b 1
)

REM Vérifier ngrok
ngrok version >NUL 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ngrok requis mais non trouvé
    echo 💡 Installez ngrok depuis https://ngrok.com/download
    echo 💡 Puis configurez votre authtoken: ngrok authtoken VOTRE_TOKEN
    pause
    exit /b 1
)

echo ✅ Prérequis vérifiés

echo.
echo 🔄 Démarrage automatique de ngrok...
python start_ngrok_auto.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Erreur lors du démarrage de ngrok
    echo 💡 Vérifiez les logs ci-dessus
    pause
    exit /b 1
)

echo.
echo ✅ Ngrok démarré avec succès!
echo.
echo 📋 Actions suivantes recommandées:
echo    1. Redémarrez l'application backend si nécessaire
echo    2. Testez l'URL publique
echo    3. Configurez Facebook Developers avec la nouvelle URL
echo.

pause
exit /b 0