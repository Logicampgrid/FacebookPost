@echo off
setlocal enabledelayedexpansion

:: ===================================================================
:: SCRIPT DE VÉRIFICATION SYSTÈME FACEBOOKPOST
:: ===================================================================
:: Vérifie tous les prérequis et la configuration avant démarrage
:: ===================================================================

title FacebookPost - Vérification Système

echo.
echo ========================================
echo   FACEBOOKPOST - VÉRIFICATION SYSTÈME
echo ========================================
echo.

set "BASE_DIR=C:\FacebookPost"
set "error_count=0"

:: Fonction de logging avec couleurs
:log_check
if "%2"=="OK" (
    echo ✅ %1
) else if "%2"=="FAIL" (
    echo ❌ %1
    set /a "error_count+=1"
) else if "%2"=="WARN" (
    echo ⚠️ %1
) else (
    echo ℹ️ %1
)
goto :eof

:: ===================================================================
:: VÉRIFICATION LOGICIELS
:: ===================================================================
echo 🔍 Vérification des logiciels requis...
echo.

:: Node.js
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('node --version') do set "node_version=%%i"
    call :log_check "Node.js détecté: !node_version!" "OK"
) else (
    call :log_check "Node.js non trouvé - Téléchargez depuis https://nodejs.org" "FAIL"
)

:: Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version') do set "python_version=%%i"
    call :log_check "Python détecté: !python_version!" "OK"
) else (
    call :log_check "Python non trouvé - Téléchargez depuis https://python.org" "FAIL"
)

:: MongoDB
set "MONGO_EXE=C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe"
if exist "%MONGO_EXE%" (
    call :log_check "MongoDB 8.0 détecté" "OK"
) else (
    call :log_check "MongoDB non trouvé à: %MONGO_EXE%" "FAIL"
    call :log_check "Téléchargez depuis https://www.mongodb.com/try/download/community" "INFO"
)

:: ngrok
ngrok version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%i in ('ngrok version') do set "ngrok_version=%%i"
    call :log_check "ngrok détecté: !ngrok_version!" "OK"
) else (
    call :log_check "ngrok non trouvé - Téléchargez depuis https://ngrok.com" "FAIL"
)

echo.

:: ===================================================================
:: VÉRIFICATION STRUCTURE DOSSIERS
:: ===================================================================
echo 📁 Vérification de la structure des dossiers...
echo.

:: Dossier principal
if exist "%BASE_DIR%" (
    call :log_check "Dossier principal: %BASE_DIR%" "OK"
) else (
    call :log_check "Dossier principal manquant: %BASE_DIR%" "FAIL"
)

:: Backend
if exist "%BASE_DIR%\backend" (
    call :log_check "Dossier backend: %BASE_DIR%\backend" "OK"
) else (
    call :log_check "Dossier backend manquant" "FAIL"
)

:: Frontend
if exist "%BASE_DIR%\frontend" (
    call :log_check "Dossier frontend: %BASE_DIR%\frontend" "OK"
) else (
    call :log_check "Dossier frontend manquant" "FAIL"
)

:: Logs
if exist "%BASE_DIR%\logs" (
    call :log_check "Dossier logs: %BASE_DIR%\logs" "OK"
) else (
    call :log_check "Dossier logs manquant - sera créé automatiquement" "WARN"
)

:: MongoDB data
if exist "C:\data\db" (
    call :log_check "Dossier MongoDB data: C:\data\db" "OK"
) else (
    call :log_check "Dossier MongoDB data manquant: C:\data\db" "FAIL"
)

echo.

:: ===================================================================
:: VÉRIFICATION FICHIERS CONFIGURATION
:: ===================================================================
echo ⚙️ Vérification des fichiers de configuration...
echo.

:: Backend .env
if exist "%BASE_DIR%\backend\.env" (
    call :log_check "Configuration backend (.env)" "OK"
    
    :: Vérifier tokens dans .env
    findstr /C:"FB_ACCESS_TOKEN_" "%BASE_DIR%\backend\.env" | findstr /V /C:"<TOKEN" >nul
    if %errorlevel% equ 0 (
        call :log_check "Tokens Facebook configurés" "OK"
    ) else (
        call :log_check "Tokens Facebook non configurés (contiennent <TOKEN)" "WARN"
    )
) else (
    call :log_check "Fichier .env backend manquant" "FAIL"
)

:: Frontend .env
if exist "%BASE_DIR%\frontend\.env" (
    call :log_check "Configuration frontend (.env)" "OK"
) else (
    call :log_check "Fichier .env frontend manquant" "FAIL"
)

:: Scripts de démarrage
if exist "%BASE_DIR%\start_full.bat" (
    call :log_check "Script de démarrage principal" "OK"
) else (
    call :log_check "Script start_full.bat manquant" "FAIL"
)

echo.

:: ===================================================================
:: VÉRIFICATION DÉPENDANCES
:: ===================================================================
echo 📦 Vérification des dépendances...
echo.

:: Python venv
if exist "%BASE_DIR%\backend\venv" (
    call :log_check "Environnement virtuel Python" "OK"
) else (
    call :log_check "Environnement virtuel Python manquant - sera créé" "WARN"
)

:: Node modules
if exist "%BASE_DIR%\frontend\node_modules" (
    call :log_check "Modules Node.js installés" "OK"
) else (
    call :log_check "Modules Node.js manquants - seront installés" "WARN"
)

:: Frontend build
if exist "%BASE_DIR%\frontend\build" (
    call :log_check "Build frontend disponible" "OK"
) else (
    call :log_check "Build frontend manquant - sera généré" "WARN"
)

echo.

:: ===================================================================
:: VÉRIFICATION PORTS
:: ===================================================================
echo 🌐 Vérification des ports...
echo.

:: Port 8001 (Backend)
netstat -an | findstr ":8001" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    call :log_check "Port 8001 occupé - sera libéré au démarrage" "WARN"
) else (
    call :log_check "Port 8001 disponible" "OK"
)

:: Port 3000 (Frontend)
netstat -an | findstr ":3000" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    call :log_check "Port 3000 occupé - sera libéré au démarrage" "WARN"
) else (
    call :log_check "Port 3000 disponible" "OK"
)

:: Port 27017 (MongoDB)
netstat -an | findstr ":27017" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    call :log_check "MongoDB déjà en cours d'exécution (port 27017)" "OK"
) else (
    call :log_check "MongoDB pas encore démarré" "INFO"
)

echo.

:: ===================================================================
:: VÉRIFICATION CONNECTIVITÉ
:: ===================================================================
echo 🌐 Test de connectivité Internet...
echo.

ping -n 1 google.com >nul 2>&1
if %errorlevel% equ 0 (
    call :log_check "Connexion Internet active" "OK"
) else (
    call :log_check "Problème de connexion Internet" "WARN"
)

echo.

:: ===================================================================
:: RÉSUMÉ ET RECOMMANDATIONS
:: ===================================================================
echo 📊 RÉSUMÉ DE LA VÉRIFICATION
echo ========================================

if %error_count% equ 0 (
    echo.
    echo ✅ SYSTÈME PRÊT POUR LE DÉMARRAGE !
    echo.
    echo Tous les prérequis sont satisfaits.
    echo Vous pouvez lancer start_full.bat en toute sécurité.
    echo.
) else (
    echo.
    echo ❌ %error_count% ERREUR(S) DÉTECTÉE(S)
    echo.
    echo Veuillez corriger les erreurs ci-dessus avant de continuer.
    echo Consultez le GUIDE_INSTALLATION_WINDOWS.md pour l'aide.
    echo.
)

:: Actions recommandées
echo 💡 ACTIONS RECOMMANDÉES :
echo.

if not exist "%BASE_DIR%\backend\.env" (
    echo 1. Copiez .env.windows vers .env dans le dossier backend
)

if not exist "%BASE_DIR%\frontend\.env" (
    echo 2. Copiez .env.windows vers .env dans le dossier frontend  
)

findstr /C:"<TOKEN" "%BASE_DIR%\backend\.env" >nul 2>&1
if %errorlevel% equ 0 (
    echo 3. Configurez vos vrais tokens Facebook dans backend\.env
)

if %error_count% equ 0 (
    echo 4. Lancez start_full.bat pour démarrer l'application
) else (
    echo 4. Corrigez les erreurs puis relancez cette vérification
)

echo.
echo ========================================
pause