@echo off
setlocal enabledelayedexpansion

:: ===================================================================
:: SCRIPT D'ARRÊT COMPLET FACEBOOKPOST
:: ===================================================================
:: Arrête proprement tous les services liés à FacebookPost
:: ===================================================================

title FacebookPost - Arrêt Complet

set "BASE_DIR=C:\FacebookPost"
set "LOG_FILE=%BASE_DIR%\start_full.log"

:: Fonction de logging
:log
set "timestamp=%date% %time%"
echo [%timestamp%] %~1
if exist "%LOG_FILE%" (
    echo [%timestamp%] %~1 >> "%LOG_FILE%"
)
goto :eof

call :log "🛑 ===== ARRÊT COMPLET FACEBOOKPOST ====="

echo.
echo ========================================
echo   ARRÊT DE TOUS LES SERVICES
echo ========================================
echo.

:: ===================================================================
:: ARRÊT DES PROCESSUS APPLICATIFS
:: ===================================================================
call :log "🛑 Arrêt des processus applicatifs..."

:: Backend Python
echo Recherche du backend Python...
tasklist /FI "WINDOWTITLE eq FacebookPost Backend" 2>nul | find "python" >nul
if %errorlevel% equ 0 (
    echo ✅ Arrêt du backend Python...
    taskkill /F /FI "WINDOWTITLE eq FacebookPost Backend" >nul 2>&1
    call :log "Backend Python arrêté"
) else (
    echo ℹ️ Backend Python non actif
)

:: Frontend Node.js
echo Recherche du frontend Node.js...
tasklist /FI "WINDOWTITLE eq FacebookPost Frontend" 2>nul | find "node" >nul
if %errorlevel% equ 0 (
    echo ✅ Arrêt du frontend Node.js...
    taskkill /F /FI "WINDOWTITLE eq FacebookPost Frontend" >nul 2>&1
    call :log "Frontend Node.js arrêté"
) else (
    echo ℹ️ Frontend Node.js non actif
)

:: Processus ngrok
echo Recherche de ngrok...
tasklist /FI "IMAGENAME eq ngrok.exe" 2>nul | find "ngrok" >nul
if %errorlevel% equ 0 (
    echo ✅ Arrêt de ngrok...
    taskkill /F /IM "ngrok.exe" >nul 2>&1
    call :log "Ngrok arrêté"
    timeout /t 2 /nobreak >nul
) else (
    echo ℹ️ Ngrok non actif
)

:: ===================================================================
:: LIBÉRATION DES PORTS
:: ===================================================================
call :log "🌐 Libération des ports..."

echo Vérification des ports utilisés...

:: Port 8001 (Backend)
netstat -ano | findstr ":8001" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo ⚠️ Port 8001 encore occupé, recherche du processus...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
        echo Arrêt forcé du processus %%a sur port 8001
        taskkill /F /PID %%a >nul 2>&1
    )
    call :log "Port 8001 libéré"
) else (
    echo ✅ Port 8001 libre
)

:: Port 3000 (Frontend)
netstat -ano | findstr ":3000" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo ⚠️ Port 3000 encore occupé, recherche du processus...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
        echo Arrêt forcé du processus %%a sur port 3000
        taskkill /F /PID %%a >nul 2>&1
    )
    call :log "Port 3000 libéré"
) else (
    echo ✅ Port 3000 libre
)

:: Port 4040 (ngrok web interface)
netstat -ano | findstr ":4040" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo ⚠️ Port 4040 (ngrok web) encore occupé...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":4040" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    call :log "Port 4040 libéré"
) else (
    echo ✅ Port 4040 libre
)

:: ===================================================================
:: NETTOYAGE DES FICHIERS TEMPORAIRES
:: ===================================================================
call :log "🧹 Nettoyage des fichiers temporaires..."

:: Supprimer ngrok_url.txt
if exist "%BASE_DIR%\backend\ngrok_url.txt" (
    echo Suppression de ngrok_url.txt...
    del "%BASE_DIR%\backend\ngrok_url.txt" >nul 2>&1
    call :log "Fichier ngrok_url.txt supprimé"
)

:: Nettoyer les logs anciens (optionnel)
echo Nettoyage des anciens logs...
forfiles /P "%BASE_DIR%\logs" /S /M "*.log" /D -7 /C "cmd /c del @path" >nul 2>&1
call :log "Anciens logs nettoyés (>7 jours)"

:: ===================================================================
:: OPTION D'ARRÊT MONGODB
:: ===================================================================
echo.
echo 🗄️ Gestion MongoDB...
tasklist /FI "IMAGENAME eq mongod.exe" 2>nul | find "mongod" >nul
if %errorlevel% equ 0 (
    echo MongoDB est en cours d'exécution.
    echo.
    choice /C YN /M "Voulez-vous arrêter MongoDB aussi (Y/N)?"
    if errorlevel 2 (
        echo ℹ️ MongoDB laissé en cours d'exécution
        call :log "MongoDB laissé actif"
    ) else (
        echo ✅ Arrêt de MongoDB...
        net stop MongoDB >nul 2>&1
        if %errorlevel% equ 0 (
            call :log "Service MongoDB arrêté"
        ) else (
            echo ⚠️ Arrêt forcé de MongoDB...
            taskkill /F /IM "mongod.exe" >nul 2>&1
            call :log "MongoDB arrêté (forcé)"
        )
    )
) else (
    echo ℹ️ MongoDB n'était pas actif
)

:: ===================================================================
:: VÉRIFICATION FINALE
:: ===================================================================
echo.
echo 🔍 Vérification finale...

set "processes_found=0"

tasklist /FI "WINDOWTITLE eq FacebookPost Backend" 2>nul | find "python" >nul
if %errorlevel% equ 0 set /a "processes_found+=1"

tasklist /FI "WINDOWTITLE eq FacebookPost Frontend" 2>nul | find "node" >nul
if %errorlevel% equ 0 set /a "processes_found+=1"

tasklist /FI "IMAGENAME eq ngrok.exe" 2>nul | find "ngrok" >nul
if %errorlevel% equ 0 set /a "processes_found+=1"

if %processes_found% equ 0 (
    echo ✅ Tous les processus FacebookPost ont été arrêtés
    call :log "Arrêt complet réussi"
) else (
    echo ⚠️ %processes_found% processus encore actifs
    call :log "Arrêt partiel - %processes_found% processus restants"
    
    echo.
    echo Processus encore actifs :
    tasklist /FI "WINDOWTITLE eq FacebookPost Backend" 2>nul | find "python"
    tasklist /FI "WINDOWTITLE eq FacebookPost Frontend" 2>nul | find "node"  
    tasklist /FI "IMAGENAME eq ngrok.exe" 2>nul | find "ngrok"
)

:: ===================================================================
:: RÉSUMÉ
:: ===================================================================
echo.
echo ========================================
echo   ARRÊT TERMINÉ
echo ========================================

call :log "✅ ===== ARRÊT COMPLET TERMINÉ ====="

echo.
echo 📊 RÉSUMÉ :
echo • Backend Python : Arrêté
echo • Frontend Node.js : Arrêté  
echo • Ngrok : Arrêté
echo • Ports 8001, 3000, 4040 : Libérés
echo • Fichiers temporaires : Nettoyés

if %processes_found% equ 0 (
    echo.
    echo ✅ Arrêt complet réussi !
    echo Vous pouvez maintenant relancer start_full.bat
) else (
    echo.
    echo ⚠️ Arrêt partiel
    echo Redémarrez Windows si des processus persistent
)

echo.
echo Log complet : %LOG_FILE%
echo ========================================

timeout /t 5 /nobreak >nul