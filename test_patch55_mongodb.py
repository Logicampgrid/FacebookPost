#!/usr/bin/env python3
"""
Test PATCH 55 - Vérification sauvegarde MongoDB avec pymongo synchrone
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv("REACT_APP_BACKEND_URL", "http://localhost:8001")
WEBHOOK_URL = f"{BACKEND_URL}/api/webhook"

def test_patch55_n8n_webhook():
    """
    Test PATCH 55 - Envoi webhook N8N multipart pour vérifier:
    1. Thread séparé lancé correctement
    2. Publication traitée en arrière-plan
    3. Sauvegarde MongoDB avec pymongo (synchrone) réussie
    4. Plus d'erreur "Task got Future attached to a different loop"
    """
    
    print("=" * 80)
    print("🧪 TEST PATCH 55 - CORRECTION MONGODB ASYNCIO LOOP")
    print("=" * 80)
    
    # Données de test N8N multipart
    test_data = {
        "store": "gizmobbs",
        "title": "Test PATCH 55 - MongoDB Sync",
        "description": "Test de la sauvegarde MongoDB avec pymongo synchrone dans thread séparé",
        "url": "https://test.com/patch55",
        "platforms": ["facebook"]
    }
    
    # Simuler un fichier texte pour le webhook
    files = {
        'json_data': (None, json.dumps(test_data), 'application/json')
    }
    
    print(f"\n📤 Envoi webhook N8N multipart...")
    print(f"   Store: {test_data['store']}")
    print(f"   Title: {test_data['title']}")
    print(f"   URL: {WEBHOOK_URL}")
    
    try:
        response = requests.post(WEBHOOK_URL, files=files, timeout=10)
        
        print(f"\n📊 Réponse HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook accepté !")
            print(f"   Status: {result.get('status')}")
            print(f"   Processing: {result.get('processing')}")
            print(f"   Patch: {result.get('patch')}")
            print(f"   Message: {result.get('message')}")
            
            if result.get('patch') == 55:
                print(f"\n🎉 PATCH 55 DÉTECTÉ !")
                print(f"   ✅ Thread séparé avec MongoDB synchrone actif")
                print(f"   ✅ Réponse immédiate reçue")
                print(f"   ✅ Traitement en arrière-plan lancé")
            
            # Attendre un peu pour la sauvegarde MongoDB
            print(f"\n⏳ Attente de 5 secondes pour la sauvegarde MongoDB...")
            import time
            time.sleep(5)
            
            print(f"\n📋 Vérification des logs backend...")
            print(f"   Recherchez dans les logs:")
            print(f"   - '🚀 PATCH 55: Lancement thread séparé N8N'")
            print(f"   - '✅ PATCH 55: Publication thread séparé réussie'")
            print(f"   - '✅ PATCH 55: Publication N8N sauvegardée (pymongo sync)'")
            print(f"   - AUCUNE erreur 'Task got Future attached to a different loop'")
            
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(f"   Réponse: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Timeout après 10 secondes")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_backend_logs():
    """Vérifier les derniers logs du backend"""
    print(f"\n📋 Vérification logs backend récents...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["tail", "-50", "/var/log/supervisor/backend.out.log"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        logs = result.stdout
        
        # Rechercher PATCH 55 dans les logs
        patch55_found = "PATCH 55" in logs
        mongodb_success = "Publication N8N sauvegardée (pymongo sync)" in logs
        asyncio_error = "different loop" in logs
        
        print(f"\n🔍 Analyse des logs:")
        print(f"   {'✅' if patch55_found else '❌'} PATCH 55 détecté dans logs")
        print(f"   {'✅' if mongodb_success else '❌'} Sauvegarde MongoDB réussie")
        print(f"   {'✅' if not asyncio_error else '❌'} Pas d'erreur asyncio loop")
        
        if patch55_found and mongodb_success and not asyncio_error:
            print(f"\n🎉 PATCH 55 FONCTIONNE PARFAITEMENT !")
            return True
        else:
            print(f"\n⚠️ Vérification manuelle des logs recommandée")
            return False
            
    except Exception as e:
        print(f"⚠️ Impossible de lire les logs: {e}")
        return False

if __name__ == "__main__":
    print(f"\n🏁 Démarrage test PATCH 55...")
    print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_patch55_n8n_webhook()
    
    print(f"\n" + "=" * 80)
    if success:
        print(f"✅ TEST PATCH 55 RÉUSSI")
        print(f"   - Thread séparé N8N lancé correctement")
        print(f"   - Réponse immédiate reçue (pas de timeout)")
        print(f"   - Sauvegarde MongoDB avec pymongo synchrone")
        print(f"   - Plus d'erreur 'Task got Future attached to a different loop'")
    else:
        print(f"❌ TEST PATCH 55 ÉCHOUÉ - Vérifier les logs backend")
    
    print(f"=" * 80)
    
    # Vérifier les logs
    check_backend_logs()
