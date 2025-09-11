@echo off
echo =========================================
echo  INSTALLATION DES DEPENDANCES - FacebookPost
echo =========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo.
    echo Veuillez installer Python 3.8+ depuis https://python.org
    echo N'oubliez pas de cocher "Add to PATH" lors de l'installation
    pause
    exit /b 1
)

REM Vérifier si Node.js est installé
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js n'est pas installé ou pas dans le PATH
    echo.
    echo Veuillez installer Node.js depuis https://nodejs.org
    pause
    exit /b 1
)

REM Vérifier si MongoDB est installé
mongod --version >nul 2>&1
if errorlevel 1 (
    echo ❌ MongoDB n'est pas installé ou pas dans le PATH
    echo.
    echo Veuillez installer MongoDB Community depuis https://mongodb.com
    pause
    exit /b 1
)

echo ✅ Vérifications préliminaires réussies
echo.

REM Installation des dépendances Python
echo 📦 Installation des dépendances Python...
cd /d "%~dp0..\backend"
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Erreur lors de l'installation des dépendances Python
    pause
    exit /b 1
)

REM Installation des dépendances Node.js
echo 📦 Installation des dépendances Node.js...
cd /d "%~dp0..\frontend"
npm install
if errorlevel 1 (
    echo ❌ Erreur lors de l'installation des dépendances Node.js
    pause
    exit /b 1
)

echo.
echo ✅ Toutes les dépendances ont été installées avec succès !
echo.
echo Prochaine étape : Exécuter 02_start_mongodb.bat
pause