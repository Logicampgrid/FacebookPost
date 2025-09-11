@echo off
echo =========================================
echo     DEMARRAGE MONGODB - FacebookPost
echo =========================================
echo.

REM Créer le répertoire data s'il n'existe pas
if not exist "%~dp0..\data" (
    echo 📁 Création du répertoire data...
    mkdir "%~dp0..\data"
)

REM Démarrer MongoDB
echo 🚀 Démarrage de MongoDB...
echo.
echo ⚠️  IMPORTANT: Laissez cette fenêtre ouverte pendant l'utilisation de l'application
echo.

cd /d "%~dp0.."
mongod --dbpath data --port 27017

REM Si on arrive ici, MongoDB s'est arrêté
echo.
echo ℹ️  MongoDB s'est arrêté
pause