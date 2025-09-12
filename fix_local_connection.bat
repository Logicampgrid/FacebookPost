@echo off
echo.
echo ============================================
echo  CORRECTION CONNEXION LOCALE
echo ============================================
echo.

echo [1/3] Vérification de la configuration...

:: Vérifier que les fichiers .env sont corrects
echo 🔍 Vérification configuration frontend...
findstr "REACT_APP_BACKEND_URL=http://localhost:8001" frontend\.env >NUL
if errorlevel 1 (
    echo ❌ Configuration frontend incorrecte
    echo 🔧 Correction en cours...
    echo # CONFIGURATION WINDOWS LOCAL avec NGROK > frontend\.env
    echo REACT_APP_BACKEND_URL=http://localhost:8001 >> frontend\.env
    echo DANGEROUSLY_DISABLE_HOST_CHECK=true >> frontend\.env
    echo ESLINT_NO_DEV_ERRORS=true >> frontend\.env
    echo HOST=0.0.0.0 >> frontend\.env
    echo PORT=3000 >> frontend\.env
    echo BROWSER=none >> frontend\.env
    echo ✅ Configuration frontend corrigée
) else (
    echo ✅ Configuration frontend OK
)

echo.
echo [2/3] Test de connexion backend...

:: Tester le backend
curl -s http://localhost:8001/api/health >NUL 2>&1
if errorlevel 1 (
    echo ❌ Backend non accessible sur http://localhost:8001
    echo.
    echo 💡 Solutions :
    echo 1. Vérifiez que le backend est démarré
    echo 2. Vérifiez qu'aucun autre processus n'utilise le port 8001
    echo 3. Relancez start_local_windows.bat
    echo.
    echo 🔍 Vérification des processus sur le port 8001...
    netstat -ano | findstr :8001
    echo.
) else (
    echo ✅ Backend accessible
    echo 📊 Réponse health check :
    curl -s http://localhost:8001/api/health
    echo.
)

echo.
echo [3/3] Test de connexion frontend...

:: Vérifier si le frontend est accessible
curl -s http://localhost:3000 >NUL 2>&1
if errorlevel 1 (
    echo ❌ Frontend non accessible sur http://localhost:3000
    echo.
    echo 💡 Solutions :
    echo 1. Allez dans le dossier frontend : cd frontend
    echo 2. Installez les dépendances : npm install
    echo 3. Démarrez le frontend : npm start
    echo.
) else (
    echo ✅ Frontend accessible
)

echo.
echo ============================================
echo.
echo 🔧 DIAGNOSTIC RÉSEAU COMPLET
echo.

echo 📡 Ports utilisés actuellement :
netstat -ano | findstr -E ":3000|:8001|:4040|:27017"

echo.
echo 🌐 Vérification ngrok (si actif) :
curl -s http://127.0.0.1:4040/api/tunnels 2>NUL | findstr public_url

echo.
echo ============================================
echo 📋 RÉSUMÉ DES ACTIONS CORRECTIVES
echo ============================================
echo.
echo Si l'erreur JSON persiste :
echo.
echo 1. ❌ "JSON.parse: unexpected character at line 1 column 1"
echo    → Le frontend reçoit du HTML au lieu de JSON
echo    → Vérifiez que REACT_APP_BACKEND_URL=http://localhost:8001
echo.
echo 2. ❌ Backend inaccessible
echo    → Lancez start_local_windows.bat
echo    → Ou manuellement : cd backend ^&^& python server.py
echo.
echo 3. ❌ Frontend ne se connecte pas
echo    → Vérifiez frontend\.env
echo    → Redémarrez le frontend : cd frontend ^&^& npm start
echo.
echo 4. ❌ Ngrok ne fonctionne pas
echo    → Utilisez votre 99_start_all_ngrok.bat
echo    → Ou lancez : ngrok http 8001
echo.
echo ============================================
echo.
pause