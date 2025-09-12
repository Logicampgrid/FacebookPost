#!/usr/bin/env python3
"""
Simulation de l'exécution du token 30KVU5Oxya5afdPt46syFR1KD65_3kxesHED2kbcHpDNW6VhT
Ce script simule l'envoi d'objets récupérés par n8n vers le webhook
"""

import requests
import json
import sys
import time
from datetime import datetime

def get_ngrok_url():
    """Récupère l'URL ngrok publique"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        response.raise_for_status()
        
        tunnels = response.json()
        if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
            return tunnels['tunnels'][0]['public_url']
        return None
    except Exception as e:
        print(f"❌ Erreur récupération URL ngrok: {e}")
        return None

def send_n8n_data(webhook_url, data):
    """Envoie des données au webhook n8n"""
    try:
        print(f"📤 Envoi vers: {webhook_url}")
        print(f"📦 Données: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            webhook_url,
            json=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "n8n-webhook-client"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Succès: {result}")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout lors de l'envoi")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def execute_token():
    """Simule l'exécution du token pour envoyer des objets n8n"""
    print("🔑 Exécution du token: 30KVU5Oxya5afdPt46syFR1KD65_3kxesHED2kbcHpDNW6VhT")
    print("=" * 70)
    
    # Récupérer l'URL ngrok
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        print("❌ Impossible de récupérer l'URL ngrok")
        return False
    
    webhook_url = f"{ngrok_url}/api/webhook/n8n"
    print(f"🌐 URL webhook: {webhook_url}")
    print()
    
    # Simulation d'objets récupérés par n8n
    n8n_objects = [
        {
            "timestamp": datetime.now().isoformat(),
            "source": "n8n_workflow",
            "workflow_id": "token_execution_001",
            "message": "🛍️ Nouveau produit ajouté au catalogue !",
            "product_url": "https://monboutique.com/produits/nouveau-article-123",
            "store": "gizmobbs",
            "platforms": ["facebook"],
            "metadata": {
                "token_used": "30KVU5Oxya5afdPt46syFR1KD65_3kxesHED2kbcHpDNW6VhT",
                "execution_id": f"exec_{int(time.time())}"
            }
        },
        {
            "timestamp": datetime.now().isoformat(),
            "source": "n8n_workflow", 
            "workflow_id": "token_execution_002",
            "content": "🎉 Promotion spéciale sur nos produits outdoor !",
            "link": "https://logicampoutdoor.com/promotions/special-week",
            "image": "https://via.placeholder.com/800x600/4CAF50/white?text=Promotion+Outdoor",
            "shop": "outdoor",
            "platforms": ["facebook", "instagram"],
            "metadata": {
                "token_used": "30KVU5Oxya5afdPt46syFR1KD65_3kxesHED2kbcHpDNW6VhT",
                "execution_id": f"exec_{int(time.time()) + 1}"
            }
        },
        {
            "timestamp": datetime.now().isoformat(),
            "source": "n8n_workflow",
            "workflow_id": "token_execution_003", 
            "text": "🏺 Découvrez notre collection antique exclusive",
            "url": "https://logicantiq.com/collections/exclusive",
            "store": "logicantiq",
            "auto_publish": True,
            "metadata": {
                "token_used": "30KVU5Oxya5afdPt46syFR1KD65_3kxesHED2kbcHpDNW6VhT",
                "execution_id": f"exec_{int(time.time()) + 2}"
            }
        }
    ]
    
    success_count = 0
    
    for i, obj in enumerate(n8n_objects, 1):
        print(f"📨 Envoi de l'objet {i}/{len(n8n_objects)}")
        
        if send_n8n_data(webhook_url, obj):
            success_count += 1
            print(f"✅ Objet {i} traité avec succès")
        else:
            print(f"❌ Échec pour l'objet {i}")
        
        if i < len(n8n_objects):
            print("⏳ Attente 3 secondes...\n")
            time.sleep(3)
        else:
            print()
    
    # Résultats finaux
    print("📊 RÉSULTATS DE L'EXÉCUTION")
    print("=" * 30)
    print(f"✅ Objets envoyés avec succès: {success_count}/{len(n8n_objects)}")
    print(f"🌐 URL webhook utilisée: {webhook_url}")
    print(f"🔑 Token: 30KVU5Oxya5afdPt46syFR1KD65_3kxesHED2kbcHpDNW6VhT")
    
    if success_count == len(n8n_objects):
        print("\n🎉 TOUS LES OBJETS ONT ÉTÉ ENVOYÉS AVEC SUCCÈS !")
        print("📱 Vérifiez vos réseaux sociaux pour voir les publications")
        return True
    else:
        print(f"\n⚠️ {len(n8n_objects) - success_count} objet(s) ont échoué")
        return False

if __name__ == "__main__":
    success = execute_token()
    sys.exit(0 if success else 1)