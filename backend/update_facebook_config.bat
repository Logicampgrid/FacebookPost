@echo off
REM ===============================================
REM Configuration Facebook AutoGPT - Meta Publishing Platform
REM Permet de modifier facilement les paramètres Facebook
REM ===============================================

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo   Configuration Facebook AutoGPT
echo ==========================================
echo.
echo 💡 Ce script permet de mettre à jour les paramètres
echo    Facebook AutoGPT dans le fichier .env
echo.

REM Vérifier que le fichier .env existe
if not exist ".env" (
    echo ❌ ERREUR: Fichier .env non trouvé dans le répertoire courant
    echo 💡 Assurez-vous d'exécuter ce script depuis le dossier backend
    pause
    exit /b 1
)

echo 📁 Fichier .env trouvé: %CD%\.env
echo.

REM Afficher les valeurs actuelles
echo 🔍 Configuration Facebook AutoGPT actuelle:
echo ----------------------------------------
findstr "FACEBOOK_APP_ID=" .env 2>nul
findstr "FACEBOOK_APP_SECRET=" .env 2>nul  
findstr "FACEBOOK_CLIENT_TOKEN=" .env 2>nul
echo.

REM Demander confirmation pour continuer
set /p "continue=Voulez-vous modifier ces paramètres ? (O/N): "
if /i not "%continue%"=="O" if /i not "%continue%"=="o" (
    echo ℹ️ Modification annulée
    pause
    exit /b 0
)

echo.
echo 📝 Saisie des nouveaux paramètres Facebook AutoGPT:
echo --------------------------------------------------

REM Saisir les nouveaux paramètres
set /p "new_app_id=📱 Nouvel App ID Facebook (actuel: 5664227323683118): "
set /p "new_app_secret=🔐 Nouvelle clé secrète (actuel: b359a1c87c920288385daf75aed873a3): "
set /p "new_client_token=🎫 Nouveau token client (actuel: 7725f6e0b13d367a829b44ff16a3421f): "

REM Valeurs par défaut si rien n'est saisi
if "%new_app_id%"=="" set "new_app_id=5664227323683118"
if "%new_app_secret%"=="" set "new_app_secret=b359a1c87c920288385daf75aed873a3"
if "%new_client_token%"=="" set "new_client_token=7725f6e0b13d367a829b44ff16a3421f"

echo.
echo 🔄 Nouveaux paramètres à appliquer:
echo ----------------------------------
echo App ID: %new_app_id%
echo Clé secrète: %new_app_secret%
echo Token client: %new_client_token%
echo.

set /p "confirm=Confirmer ces modifications ? (O/N): "
if /i not "%confirm%"=="O" if /i not "%confirm%"=="o" (
    echo ℹ️ Modification annulée
    pause
    exit /b 0
)

echo.
echo 🔧 Application des modifications...

REM Créer une sauvegarde du fichier .env
copy ".env" ".env.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%" >nul 2>&1
echo ✅ Sauvegarde créée: .env.backup.[timestamp]

REM Appliquer les modifications au fichier .env
REM Créer un fichier temporaire pour les modifications
echo 🔄 Mise à jour du fichier .env...

REM Lire le fichier .env et appliquer les modifications
set "temp_file=.env.temp"
if exist "%temp_file%" del "%temp_file%"

for /f "delims=" %%a in (.env) do (
    set "line=%%a"
    
    if "!line:~0,16!"=="FACEBOOK_APP_ID=" (
        echo FACEBOOK_APP_ID=%new_app_id%>>"%temp_file%"
    ) else if "!line:~0,20!"=="FACEBOOK_APP_SECRET=" (
        echo FACEBOOK_APP_SECRET=%new_app_secret%>>"%temp_file%"
    ) else if "!line:~0,22!"=="FACEBOOK_CLIENT_TOKEN=" (
        echo FACEBOOK_CLIENT_TOKEN=%new_client_token%>>"%temp_file%"
    ) else (
        echo !line!>>"%temp_file%"
    )
)

REM Remplacer le fichier .env original
move "%temp_file%" ".env" >nul 2>&1

if %errorlevel% equ 0 (
    echo ✅ Configuration Facebook AutoGPT mise à jour avec succès!
    echo.
    
    echo 🔍 Nouvelle configuration:
    echo -------------------------
    findstr "FACEBOOK_APP_ID=" .env
    findstr "FACEBOOK_APP_SECRET=" .env
    findstr "FACEBOOK_CLIENT_TOKEN=" .env
    echo.
    
    REM Demander s'il faut redémarrer le backend
    set /p "restart=Redémarrer le backend pour appliquer les changements ? (O/N): "
    if /i "!restart!"=="O" if /i "!restart!"=="o" (
        echo 🔄 Redémarrage du backend...
        
        REM Tenter d'arrêter le processus Python existant
        taskkill /f /im python.exe /fi "WINDOWTITLE eq *server_windows*" >nul 2>&1
        timeout /t 2 /nobreak >nul
        
        echo 🚀 Démarrage du backend avec la nouvelle configuration...
        echo 💡 Utilisez start_backend.bat pour démarrer le serveur
        echo.
    )
    
    echo ✅ Configuration terminée avec succès!
    
) else (
    echo ❌ ERREUR: Impossible de mettre à jour le fichier .env
    echo 💡 Vérifiez les permissions du fichier
    if exist ".env.backup.*" echo 🔄 Restaurez depuis la sauvegarde si nécessaire
)

echo.
echo 📋 Résumé des actions:
echo ---------------------
echo ✅ Sauvegarde du fichier .env original
echo ✅ Mise à jour des paramètres Facebook AutoGPT
echo 💡 Pour utiliser la nouvelle configuration, redémarrez le backend
echo.

pause