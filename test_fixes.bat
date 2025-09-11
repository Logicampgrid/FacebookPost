@echo off
setlocal enabledelayedexpansion

:: ===================================================================
:: SCRIPT DE TEST DES CORRECTIONS FACEBOOKPOST
:: ===================================================================
:: Teste rapidement que les corrections fonctionnent
:: ===================================================================

title FacebookPost - Test des Corrections

echo.
echo ========================================
echo   TEST DES CORRECTIONS FACEBOOKPOST
echo ========================================
echo.

set "BASE_DIR=C:\FacebookPost"
set "BACKEND_DIR=%BASE_DIR%\backend"

:: Fonction de logging
:log
set "timestamp=%time%"
echo [%timestamp%] %~1
goto :eof

call :log "🔍 Test des corrections..."

:: ===================================================================
:: TEST 1: VÉRIFIER SERVEUR BACKEND
:: ===================================================================
call :log "1. Test backend localhost:8001..."

curl -s -i http://localhost:8001/api/health >nul 2>&1
if %errorlevel% equ 0 (
    call :log "✅ Backend répond sur localhost:8001"
    
    :: Tester réponse JSON
    curl -s http://localhost:8001/api/health > temp_response.json 2>&1
    if exist temp_response.json (
        findstr "status" temp_response.json >nul
        if !errorlevel! equ 0 (
            call :log "✅ Réponse JSON valide détectée"
        ) else (
            call :log "❌ Réponse pas JSON valide"
            type temp_response.json
        )
        del temp_response.json >nul 2>&1
    )
) else (
    call :log "❌ Backend non accessible sur localhost:8001"
)

:: ===================================================================
:: TEST 2: VÉRIFIER URL NGROK
:: ===================================================================
call :log "2. Test URL ngrok..."

if exist "%BACKEND_DIR%\ngrok_url.txt" (
    set /p ngrok_url=<"%BACKEND_DIR%\ngrok_url.txt"
    call :log "✅ Fichier ngrok_url.txt trouvé: !ngrok_url!"
    
    if not "!ngrok_url!"=="" (
        echo !ngrok_url! | findstr /B "https://" >nul
        if !errorlevel! equ 0 (
            call :log "✅ URL ngrok valide (commence par https://)"
            
            :: Tester l'URL ngrok
            curl -s -I "!ngrok_url!/api/health" >nul 2>&1
            if !errorlevel! equ 0 (
                call :log "✅ URL ngrok accessible"
            ) else (
                call :log "❌ URL ngrok non accessible"
            )
        ) else (
            call :log "❌ URL ngrok invalide (ne commence pas par https://)"
        )
    ) else (
        call :log "❌ Fichier ngrok_url.txt vide"
    )
) else (
    call :log "❌ Fichier ngrok_url.txt non trouvé"
)

:: ===================================================================
:: TEST 3: VÉRIFIER PROCESSUS ACTIFS
:: ===================================================================
call :log "3. Test processus actifs..."

tasklist /FI "IMAGENAME eq python.exe" | find "python" >nul
if %errorlevel% equ 0 (
    call :log "✅ Processus Python actif"
) else (
    call :log "❌ Aucun processus Python détecté"
)

tasklist /FI "IMAGENAME eq node.exe" | find "node" >nul
if %errorlevel% equ 0 (
    call :log "✅ Processus Node.js actif"
) else (
    call :log "❌ Aucun processus Node.js détecté"
)

tasklist /FI "IMAGENAME eq ngrok.exe" | find "ngrok" >nul
if %errorlevel% equ 0 (
    call :log "✅ Processus ngrok actif"
) else (
    call :log "❌ Aucun processus ngrok détecté"
)

:: ===================================================================
:: TEST 4: VÉRIFIER PORTS
:: ===================================================================
call :log "4. Test ports..."

netstat -an | findstr ":8001" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    call :log "✅ Port 8001 en écoute (Backend)"
) else (
    call :log "❌ Port 8001 non ouvert"
)

netstat -an | findstr ":3000" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    call :log "✅ Port 3000 en écoute (Frontend)"
) else (
    call :log "❌ Port 3000 non ouvert"
)

:: ===================================================================
:: RÉSUMÉ
:: ===================================================================
echo.
echo ========================================
echo   RÉSUMÉ DU TEST
echo ========================================
echo.

call :log "🎯 RECOMMANDATIONS:"
echo.

curl -s http://localhost:8001/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Les corrections semblent fonctionner !
    echo.
    echo 💡 Prochaines étapes :
    echo    1. Testez l'interface sur localhost:3000
    echo    2. Testez l'interface via l'URL ngrok
    echo    3. Vérifiez la connexion Facebook
) else (
    echo ❌ Le backend ne répond pas correctement
    echo.
    echo 💡 Actions nécessaires :
    echo    1. Vérifiez que start_full.bat est lancé
    echo    2. Consultez les logs dans start_full.log
    echo    3. Redémarrez avec backend_restart.bat
)

echo.
echo ========================================
pause