@echo off
echo =====================================
echo   INSTALLATION MODULE SCHEDULE 
echo =====================================
echo.
echo 🎯 Ce script installe le module 'schedule' pour le nettoyage automatique
echo 💡 Optionnel - le serveur fonctionne sans ce module
echo.
echo 🔍 Vérification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python non trouvé dans PATH
    echo 💡 Assurez-vous que Python est installé et dans le PATH
    pause
    exit /b 1
)

echo ✅ Python détecté
echo.
echo 📦 Installation du module schedule...
pip install schedule

if errorlevel 1 (
    echo ❌ Erreur installation
    echo 💡 Essayez: python -m pip install schedule
    pause
    exit /b 1
)

echo ✅ Module schedule installé avec succès !
echo.
echo 🎯 Avantages du module schedule:
echo   • Nettoyage automatique toutes les 30 minutes
echo   • Suppression différée des fichiers après 2h
echo   • Gestion automatique de l'espace disque
echo.
echo 💡 Alternative sans schedule:
echo   • Nettoyage manuel via: curl -X POST http://localhost:8001/api/cleanup
echo   • Ou suppression manuelle des fichiers webhook anciens
echo.
echo 🚀 Redémarrez le serveur pour activer le nettoyage automatique
echo.
pause