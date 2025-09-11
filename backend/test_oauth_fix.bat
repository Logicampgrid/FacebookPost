@echo off
REM ===============================================
REM Test correction OAuth Facebook
REM ===============================================

echo.
echo ====================================
echo   Test OAuth Facebook Correction
echo ====================================
echo.

echo 🧪 Test 1: Format JSON
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code -H "Content-Type: application/json" -d "{\"code\": \"TEST123\", \"state\": \"TESTSTATE\"}"

echo.
echo.
echo 🧪 Test 2: Format Form-data
curl -X POST http://localhost:8001/api/auth/facebook/exchange-code -H "Content-Type: application/x-www-form-urlencoded" -d "code=TEST456&state=TESTSTATE2"

echo.
echo.
echo 🧪 Test 3: Health Check
curl http://localhost:8001/api/health

echo.
echo.
echo ✅ Tests terminés
echo 💡 Si vous voyez "success": false avec une erreur Facebook OAuth, c'est normal (code de test invalide)
echo 💡 L'important est de recevoir un status 200 et non 400
echo.

pause