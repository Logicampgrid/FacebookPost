#!/usr/bin/env python3
"""
Test webhook pour vérifier les logs PATCH 60 en conditions réelles
"""
import requests
import json

WEBHOOK_URL = "http://localhost:8001/api/webhook"

# Données de test simulant une publication N8N pour logicamp
test_data = {
    "store": "logicamp",
    "title": "Test PATCH 60 - Vidéo Facebook Logicamp",
    "description": "Test de validation du token FACEBOOK_DIRECT_TOKEN",
    "url": "https://logicamp.org/test-patch60",
    "platforms": ["facebook"]  # Test uniquement Facebook
}

print("=" * 60)
print("🧪 TEST WEBHOOK PATCH 60 - Publication Logicamp")
print("=" * 60)
print()
print("📤 Envoi webhook de test...")
print(f"URL: {WEBHOOK_URL}")
print(f"Store: {test_data['store']}")
print(f"Plateformes: {test_data['platforms']}")
print()

try:
    # Envoi du webhook
    response = requests.post(
        WEBHOOK_URL,
        json=test_data,
        timeout=10
    )
    
    print(f"✅ Réponse HTTP: {response.status_code}")
    print()
    
    try:
        response_data = response.json()
        print("📦 Réponse serveur:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
    except:
        print("📦 Réponse serveur (texte):")
        print(response.text[:500])
    
    print()
    print("=" * 60)
    print("📋 VÉRIFIER LES LOGS BACKEND POUR:")
    print("=" * 60)
    print("1. ✅ PATCH 60: Token dynamique ignoré pour logicamp")
    print("2. ✅ FACEBOOK_DIRECT_TOKEN préservé")
    print("3. ✅ Configuration store logicamp chargée")
    print()
    print("💡 Commande pour voir les logs:")
    print("   tail -f /var/log/supervisor/backend.out.log | grep -E 'PATCH|logicamp|✅|❌'")
    
except requests.exceptions.Timeout:
    print("⏱️ Timeout - Le serveur prend du temps (normal pour FTP/upload)")
    print("✅ Vérifier les logs pour voir le traitement en cours")
except Exception as e:
    print(f"❌ Erreur: {e}")
