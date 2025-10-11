@echo off
REM Script de vérification des PATCH sur serveur Windows
REM Vérifie automatiquement que tous les PATCH 45-60 sont appliqués

echo.
echo ========================================================================
echo    VERIFICATION DES PATCH - Serveur Windows
echo ========================================================================
echo.

REM Définir le chemin du fichier server.py
set SERVER_PATH=C:\FacebookPost\backend\server.py

REM Vérifier si le fichier existe
if not exist "%SERVER_PATH%" (
    echo [ERREUR] Fichier server.py non trouve: %SERVER_PATH%
    echo.
    echo Veuillez modifier le chemin dans ce fichier batch:
    echo    verifier_patch_windows.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Fichier analyse: %SERVER_PATH%
echo.

REM Exécuter le script Python de vérification
python verifier_patch_windows.py "%SERVER_PATH%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================================
    echo    VERIFICATION REUSSIE - Tous les PATCH sont appliques
    echo ========================================================================
    echo.
    echo Prochaines etapes:
    echo   1. Redemarrer le serveur backend
    echo   2. Verifier les logs de demarrage
    echo   3. Tester les publications N8N
    echo.
) else (
    echo.
    echo ========================================================================
    echo    VERIFICATION ECHOUEE - Certains PATCH sont manquants
    echo ========================================================================
    echo.
    echo Consultez le guide d'application:
    echo   GUIDE_APPLICATION_PATCH_WINDOWS.md
    echo.
)

echo.
pause
