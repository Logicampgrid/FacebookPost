@echo off
REM ===============================================
REM Test des publications automatiques - Meta Publishing Platform
REM Teste les 3 stores : gizmobbs, logicantiq, outdoor
REM ===============================================

echo.
echo ==========================================
echo   Test Publications Automatiques  
echo ==========================================
echo.
echo 🧪 Test des publications pour les 3 stores:
echo    • gizmobbs → Le Berger Blanc Suisse
echo    • logicantiq → LogicAntiq  
echo    • outdoor → Logicamp Outdoor
echo.

REM Vérifier que le backend est démarré
echo 🔍 Vérification du backend...
curl -s http://localhost:8001/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERREUR: Backend non accessible sur http://localhost:8001
    echo 💡 Démarrez d'abord le backend avec start_backend.bat
    pause
    exit /b 1
)

echo ✅ Backend accessible
echo.

echo 📱 Test publication Facebook pour les 3 stores...
echo ================================================

curl -X POST http://localhost:8001/api/post/test ^
  -H "Content-Type: application/json" ^
  -d "{\"platforms\": [\"facebook\"], \"custom_message\": \"Test automatique 🚀 - %date% %time%\"}"

echo.
echo.
echo 📋 Résumé du test:
echo ================
echo ✅ Publication Facebook testée pour les 3 stores
echo ℹ️  Instagram nécessite une image (pas testé ici)
echo 💡 Vérifiez les pages Facebook pour confirmer les publications
echo.
echo 🔗 Pages Facebook à vérifier:
echo   • Le Berger Blanc Suisse: https://facebook.com/102401876209415
echo   • LogicAntiq: https://facebook.com/210654558802531
echo   • Logicamp Outdoor: https://facebook.com/236260991673388
echo.

pause