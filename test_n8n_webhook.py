#!/usr/bin/env python3
"""
Script de test pour le webhook n8n
Simule l'envoi de données depuis n8n vers le webhook
"""

import requests
import json
import sys
import time

def get_ngrok_url():
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        response.raise_for_status()
        
        tunnels = response.json()
        if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
            return tunnels['tunnels'][0]['public_url']
        return None
    except:
        return None

def test_n8n_webhook():
    # Récupérer l'URL ngrok
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        print("❌ Impossible de récupérer l'URL ngrok")
        return False
    
    webhook_url = f"{ngrok_url}/api/webhook/n8n"
    print(f"🔗 URL webhook n8n: {webhook_url}")
    
    # Tests avec différents types de données
    test_cases = [
        {
            "name": "Publication Facebook simple",
            "data": {
                "message": "🎯 Test de publication automatique depuis n8n !",
                "product_url": "https://example.com/produit-1",
                "store": "gizmobbs",
                "platforms": ["facebook"],
                "source": "n8n_test"
            }
        },
        {
            "name": "Publication multi-plateformes",
            "data": {
                "message": "🚀 Publication sur Facebook et Instagram !",
                "product_url": "https://example.com/produit-2",
                "image_url": "https://via.placeholder.com/800x600.jpg",
                "store": "logicantiq",
                "platforms": ["facebook", "instagram"],
                "source": "n8n_multi"
            }
        },
        {
            "name": "Données n8n avec noms alternatifs",
            "data": {
                "content": "📦 Nouveau produit disponible !",
                "link": "https://example.com/produit-3",
                "shop": "outdoor",
                "source": "n8n_alt_names"
            }
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}/3: {test_case['name']}")
        print(f"📤 Données: {json.dumps(test_case['data'], indent=2)}")
        
        try:
            response = requests.post(
                webhook_url,
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Succès: {result}")
                success_count += 1
            else:
                print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # Attendre entre les tests
        if i < len(test_cases):
            print("⏳ Attente 5 secondes...")
            time.sleep(5)
    
    print(f"\n📊 Résultats: {success_count}/{len(test_cases)} tests réussis")
    return success_count == len(test_cases)

if __name__ == "__main__":
    print("🚀 Test du webhook n8n")
    print("=" * 50)
    
    success = test_n8n_webhook()
    if success:
        print("\n🎉 Tous les tests ont réussi !")
    else:
        print("\n⚠️ Certains tests ont échoué")
        sys.exit(1)