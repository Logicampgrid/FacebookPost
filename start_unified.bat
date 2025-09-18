@echo off
echo ===============================================
echo    Meta Publishing Platform - Configuration Unifiee
echo ===============================================
echo.

cd /d "%~dp0"

echo [INFO] Demarrage de l'application unifiee...
python start_unified.py

echo.
echo [INFO] Application arretee.
pause