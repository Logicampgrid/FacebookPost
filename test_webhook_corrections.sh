#!/bin/bash

echo "🧪 Test Webhook - Corrections Session 2"
echo "======================================"

BASE_URL="http://localhost:8001"

# Fonction utilitaire pour tester un endpoint
test_endpoint() {
    local endpoint=$1
    local method=${2:-GET}
    local description=$3
    
    echo -n "Testing $description... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint" 2>/dev/null)
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" 2>/dev/null)
    fi
    
    if [ "$response" = "200" ]; then
        echo "✅ ($response)"
    elif [ "$response" = "000" ]; then
        echo "⚠️  Serveur non démarré"
    else
        echo "❌ ($response)"
    fi
}

echo ""
echo "1. 🔌 Test des endpoints de base"
echo "--------------------------------"
test_endpoint "/api/health" "GET" "Health check"
test_endpoint "/api/test-ftp" "GET" "Test FTP connection"  
test_endpoint "/api/test-gizmobbs" "GET" "Test store gizmobbs"

echo ""
echo "2. 🎥 Test webhook vidéo (simulation)"
echo "-----------------------------------"

# Créer un fichier vidéo factice pour test
echo "Création fichier test vidéo..."
echo "fake video content" > test_video.mp4

# Test publication vidéo
echo -n "Test webhook vidéo Facebook... "
response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST \
    -F "store=gizmobbs" \
    -F "title=Test Vidéo Session 2" \
    -F "url=https://example.com" \
    -F "description=Test correction détection vidéo" \
    -F "file=@test_video.mp4" \
    "$BASE_URL/api/webhook" 2>/dev/null)

if [ "$response" = "200" ]; then
    echo "✅ ($response)"
elif [ "$response" = "000" ]; then
    echo "⚠️  Serveur non démarré" 
else
    echo "❌ ($response)"
fi

echo ""
echo "3. 🖼️ Test webhook image Instagram"
echo "--------------------------------"

# Créer une image factice pour test
echo "Création fichier test image..."
echo "fake image content" > test_image.jpg

echo -n "Test webhook image Instagram... "
response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST \
    -F "store=gizmobbs" \
    -F "title=Test Image Instagram Session 2" \
    -F "url=https://example.com" \
    -F "description=Test correction FTP Instagram" \
    -F "file=@test_image.jpg" \
    "$BASE_URL/api/webhook" 2>/dev/null)

if [ "$response" = "200" ]; then
    echo "✅ ($response)"
elif [ "$response" = "000" ]; then
    echo "⚠️  Serveur non démarré"
else
    echo "❌ ($response)" 
fi

echo ""
echo "4. 📋 Format n8n webhook"
echo "------------------------"

echo -n "Test format n8n (jsonData + file)... "
response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST \
    -F 'jsonData={"store":"gizmobbs","title":"Test n8n","url":"https://example.com","description":"Test n8n format"}' \
    -F "file=@test_image.jpg" \
    "$BASE_URL/api/webhook" 2>/dev/null)

if [ "$response" = "200" ]; then
    echo "✅ ($response)"
elif [ "$response" = "000" ]; then
    echo "⚠️  Serveur non démarré"
else
    echo "❌ ($response)"
fi

echo ""
echo "🧹 Nettoyage fichiers de test"
echo "-----------------------------"
rm -f test_video.mp4 test_image.jpg
echo "✅ Fichiers supprimés"

echo ""
echo "======================================"
echo "📊 RÉSUMÉ"
echo "======================================"
echo "✅ Corrections appliquées:"
echo "   • Détection vidéo par MIME type"
echo "   • FTP retry robuste (4 configs)"
echo "   • Polling OAuth optimisé (120s)"
echo ""
echo "🔧 Pour démarrer le serveur:"
echo "   cd /app/backend && python server.py"
echo ""
echo "📖 Guide complet: /app/GUIDE_TEST_CORRECTIONS.md"
echo "======================================"