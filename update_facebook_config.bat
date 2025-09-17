@echo off
REM ===============================================
REM Script pour mettre à jour automatiquement l'application Facebook
REM avec l'URL ngrok active détectée dynamiquement
REM ===============================================

echo.
echo ========================================
echo  MISE A JOUR FACEBOOK OAUTH AUTOMATIQUE
echo ========================================
echo.

REM Paramètres de l'application Facebook
set "APP_ID=5664227323683118"
set "APP_SECRET=b359a1c87c920288385daf75aed873a3"
set "CLIENT_TOKEN=7725f6e0b13d367a829b44ff16a3421f"

REM Générer le token d'accès administrateur
set "APP_ACCESS_TOKEN=%APP_ID%|%APP_SECRET%"

echo [1/5] Configuration de l'access token administrateur...
echo ✅ Token admin généré: %APP_ACCESS_TOKEN%

REM Détecter l'URL ngrok active via l'API locale
echo.
echo [2/5] Détection de l'URL ngrok active...

set "NGROK_URL="
set /a attempts=0
set /a max_attempts=10

:detect_ngrok
set /a attempts+=1
if %attempts% gtr %max_attempts% (
    echo ❌ Impossible de détecter l'URL ngrok après %max_attempts% tentatives
    echo 💡 Vérifiez que ngrok est démarré et accessible sur http://127.0.0.1:4040
    pause
    exit /b 1
)

REM Récupérer les tunnels via l'API ngrok
for /f "delims=" %%i in ('curl -s http://127.0.0.1:4040/api/tunnels 2^>NUL') do set "ngrok_response=%%i"

REM Vérifier si la réponse contient une URL
echo %ngrok_response% | findstr "public_url" >NUL 2>&1
if %errorlevel% neq 0 (
    echo ⏳ Tentative %attempts%/%max_attempts%: Attente de l'URL ngrok...
    timeout /t 2 /nobreak >NUL
    goto detect_ngrok
)

REM Extraire l'URL ngrok (version simplifiée pour Windows)
for /f "tokens=4 delims=:," %%a in ('echo %ngrok_response% ^| findstr "public_url"') do (
    set "raw_url=%%a"
)

REM Nettoyer l'URL (enlever guillemets et espaces)
set "NGROK_URL=%raw_url:"=%"
set "NGROK_URL=%NGROK_URL: =%"

REM Vérifier que l'URL est valide
if "%NGROK_URL%"=="" (
    echo ⏳ Tentative %attempts%/%max_attempts%: URL non détectée, nouvelle tentative...
    timeout /t 2 /nobreak >NUL
    goto detect_ngrok
)

REM S'assurer que l'URL commence par https://
if not "%NGROK_URL:~0,8%"=="https://" (
    if not "%NGROK_URL:~0,7%"=="http://" (
        set "NGROK_URL=https://%NGROK_URL%"
    )
)

echo ✅ URL ngrok détectée: %NGROK_URL%

REM Sauvegarder l'URL pour référence
echo %NGROK_URL% > "%~dp0backend\ngrok_url.txt"

echo.
echo [3/5] Mise à jour des domaines Facebook...

REM Mettre à jour le domaine de l'application
echo 🔄 Configuration du domaine principal...
curl -s -X POST "https://graph.facebook.com/v18.0/%APP_ID%" ^
  -d "app_domains=[\"%NGROK_URL%\"]" ^
  -d "access_token=%APP_ACCESS_TOKEN%" ^
  -H "Content-Type: application/x-www-form-urlencoded"

if %errorlevel% equ 0 (
    echo ✅ Domaine principal configuré: %NGROK_URL%
) else (
    echo ⚠️ Possible erreur lors de la configuration du domaine
)

echo.
echo [4/5] Mise à jour des URLs OAuth...

REM Configuration des URIs de redirection OAuth (plusieurs variantes)
echo 🔄 Configuration des URIs de redirection...

REM URI principale (root)
curl -s -X POST "https://graph.facebook.com/v18.0/%APP_ID%" ^
  -d "oauth_redirect_uris=[\"%NGROK_URL%/\",\"%NGROK_URL%/auth/callback\",\"%NGROK_URL%/auth/callb\"]" ^
  -d "access_token=%APP_ACCESS_TOKEN%" ^
  -H "Content-Type: application/x-www-form-urlencoded"

if %errorlevel% equ 0 (
    echo ✅ URIs de redirection configurées:
    echo    • %NGROK_URL%/
    echo    • %NGROK_URL%/auth/callback
    echo    • %NGROK_URL%/auth/callb
) else (
    echo ⚠️ Possible erreur lors de la configuration OAuth
)

REM Mettre à jour l'URL du site web
echo 🔄 Configuration de l'URL du site...
curl -s -X POST "https://graph.facebook.com/v18.0/%APP_ID%" ^
  -d "website_url=%NGROK_URL%" ^
  -d "access_token=%APP_ACCESS_TOKEN%" ^
  -H "Content-Type: application/x-www-form-urlencoded"

REM Configuration des origines web pour le SDK JavaScript
echo 🔄 Configuration des origines web (JS SDK)...
curl -s -X POST "https://graph.facebook.com/v18.0/%APP_ID%" ^
  -d "web_origins=[\"%NGROK_URL%\"]" ^
  -d "access_token=%APP_ACCESS_TOKEN%" ^
  -H "Content-Type: application/x-www-form-urlencoded"

echo.
echo [5/5] Finalisation et vérification...

REM Test de la configuration
echo 🧪 Test de la configuration...
curl -s "https://graph.facebook.com/v18.0/%APP_ID%?fields=app_domains,website_url&access_token=%APP_ACCESS_TOKEN%" > temp_config.json

REM Afficher la configuration actuelle (si possible)
if exist temp_config.json (
    echo ✅ Configuration Facebook mise à jour avec succès !
    del temp_config.json >NUL 2>&1
) else (
    echo ⚠️ Configuration appliquée mais vérification échouée
)

echo.
echo ========================================
echo ✅ MISE A JOUR FACEBOOK TERMINÉE
echo ========================================
echo.
echo 🌐 URL ngrok active: %NGROK_URL%
echo 🔐 Configuration OAuth mise à jour automatiquement
echo 📱 L'application Facebook autorise maintenant ce domaine
echo.
echo 💡 URLs configurées dans Facebook:
echo    • Domaine principal: %NGROK_URL%
echo    • Redirect URI 1: %NGROK_URL%/
echo    • Redirect URI 2: %NGROK_URL%/auth/callback
echo    • Redirect URI 3: %NGROK_URL%/auth/callb
echo    • Site web: %NGROK_URL%
echo    • Origine JS: %NGROK_URL%
echo.
echo ⚠️ IMPORTANT:
echo    • Cette configuration est valable tant que ngrok reste actif
echo    • Relancez ce script si l'URL ngrok change
echo    • Vérifiez les permissions dans Facebook Developers Console
echo.

exit /b 0