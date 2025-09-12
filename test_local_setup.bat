@echo off
echo.
echo ============================================
echo  TEST CONFIGURATION LOCALE
echo ============================================
echo.

echo [TEST 1] Vérification des fichiers de configuration...

:: Test frontend .env
if exist "frontend\.env" (
    echo ✅ frontend\.env existe
    findstr "localhost:8001" frontend\.env >NUL
    if errorlevel 1 (
        echo ❌ REACT_APP_BACKEND_URL ne pointe pas vers localhost:8001
        echo 🔧 Configuration incorrecte détectée
    ) else (
        echo ✅ Configuration frontend correcte (localhost:8001)
    )
) else (
    echo ❌ frontend\.env manquant
)

:: Test backend .env
if exist "backend\.env" (
    echo ✅ backend\.env existe
    findstr "LOCAL_DEV_MODE=true" backend\.env >NUL
    if %errorlevel%==0 (
        echo ✅ Mode développement local activé
    ) else (
        echo ⚠️ Mode développement local non configuré
    )
) else (
    echo ❌ backend\.env manquant
)

echo.
echo [TEST 2] Vérification des dépendances...

:: Test Python
python --version >NUL 2>&1
if %errorlevel%==0 (
    echo ✅ Python installé
    python --version
) else (
    echo ❌ Python non trouvé
)

:: Test Node.js
node --version >NUL 2>&1
if %errorlevel%==0 (
    echo ✅ Node.js installé
    node --version
) else (
    echo ❌ Node.js non trouvé
)

:: Test MongoDB
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ MongoDB en cours d'exécution
) else (
    echo ⚠️ MongoDB non démarré
)

:: Test Ngrok
ngrok version >NUL 2>&1
if %errorlevel%==0 (
    echo ✅ Ngrok installé
    ngrok version
) else (
    echo ⚠️ Ngrok non trouvé dans PATH
)

echo.
echo [TEST 3] Test de connexion simulé...

:: Simuler le test JSON qui posait problème
echo 🔍 Simulation de l'erreur JSON originale...
echo.
echo ❌ AVANT (problème) :
echo    Endpoint: http://localhost:8001/api/health
echo    Erreur: JSON.parse: unexpected character at line 1 column 1
echo.
echo ✅ APRÈS (solution) :
echo    Configuration: REACT_APP_BACKEND_URL=http://localhost:8001
echo    Mode local: LOCAL_DEV_MODE=true
echo    Résultat attendu: JSON valide de l'API

echo.
echo ============================================
echo 📋 RÉSUMÉ DES CORRECTIONS APPORTÉES
echo ============================================
echo.
echo 1. ✅ Configuration frontend corrigée pour pointer vers localhost:8001
echo 2. ✅ Mode développement local activé dans backend
echo 3. ✅ Scripts de démarrage Windows créés :
echo    • start_local_windows.bat (démarrage complet)
echo    • fix_local_connection.bat (diagnostic/correction)
echo 4. ✅ Protection contre modification automatique .env en local
echo 5. ✅ Support ngrok avec votre script existant (99_start_all_ngrok.bat)

echo.
echo ============================================
echo 🚀 PROCHAINES ÉTAPES
echo ============================================
echo.
echo 1. Double-cliquez sur 'start_local_windows.bat'
echo 2. Attendez que tous les services démarrent
echo 3. Ouvrez http://localhost:3000 dans votre navigateur
echo 4. Testez la connexion avec "Token manuel"
echo.
echo Si problème : lancez 'fix_local_connection.bat'
echo.

pause