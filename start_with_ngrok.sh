#!/bin/bash
# Script de démarrage complet pour FacebookPost avec ngrok

echo "🚀 Démarrage FacebookPost avec Ngrok"
echo "=================================="

# Fonction de logging
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# Vérifier si les services sont démarrés
log "📋 Vérification des services..."
sudo supervisorctl status | grep -E "(backend|frontend|mongodb)"

# Attendre que le backend soit prêt
log "⏳ Attente du backend..."
for i in {1..10}; do
    if curl -s http://localhost:8001/api/health > /dev/null; then
        log "✅ Backend prêt"
        break
    fi
    sleep 2
done

# Vérifier si ngrok est déjà en cours
log "🔍 Vérification de ngrok..."
if curl -s http://127.0.0.1:4040/api/tunnels > /dev/null 2>&1; then
    log "✅ Ngrok déjà actif"
    
    # Synchroniser la configuration
    log "🔄 Synchronisation de la configuration..."
    curl -s -X POST http://localhost:8001/api/sync/ngrok | python3 -m json.tool
    
else
    log "⚠️ Ngrok non détecté"
    echo ""
    echo "📝 Instructions manuelles:"
    echo "1. Ouvrez un nouveau terminal"
    echo "2. Exécutez: ngrok http 8001"
    echo "3. Puis exécutez: curl -X POST http://localhost:8001/api/sync/ngrok"
    echo ""
fi

# Afficher les URLs importantes
echo ""
log "🌐 URLs de l'application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8001"
echo "   Health:   http://localhost:8001/api/health"

# Afficher le health check
echo ""
log "📊 Status de l'application:"
curl -s http://localhost:8001/api/health | python3 -m json.tool

echo ""
echo "🎉 FacebookPost est prêt !"
echo "=================================="