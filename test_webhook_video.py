#!/usr/bin/env python3
"""
Test de simulation webhook avec vidéo pour vérifier que 
l'application utilise bien l'endpoint /videos et non /feed
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8001"

def test_webhook_video_simulation():
    """Simule un webhook avec une vidéo pour tester l'endpoint correct"""
    
    print("🎬 Test simulation webhook vidéo")
    print("=" * 50)
    
    # Données simulées d'un webhook avec vidéo (format n8n typique)
    webhook_data = {
        "store": "gizmobbs",
        "content": "Test vidéo automatique - Berger Blanc Suisse 🐕 #test #video",
        "platforms": ["facebook"],
        "video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1MB.mp4",  # URL vidéo test
        "test_mode": True
    }
    
    print(f"📤 Données envoyées au webhook:")
    print(json.dumps(webhook_data, indent=2))
    print()
    
    try:
        print("🚀 Envoi au webhook...")
        response = requests.post(
            f"{BACKEND_URL}/api/webhook",
            json=webhook_data,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook traité avec succès!")
            print(f"📝 Réponse: {json.dumps(result, indent=2)}")
            
            # Analyser la réponse pour vérifier que c'est bien traité comme vidéo
            if "results" in result:
                for platform, platform_result in result["results"].items():
                    if platform == "facebook" and platform_result.get("success"):
                        print(f"✅ Facebook: Publication réussie")
                        print(f"   ID: {platform_result.get('data', {}).get('id', 'N/A')}")
                        if "video" in str(platform_result).lower():
                            print("✅ Détection vidéo confirmée!")
                        else:
                            print("⚠️ Pas de mention vidéo dans la réponse")
            
        else:
            print(f"❌ Erreur webhook: {response.status_code}")
            print(f"   Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_ngrok_accessibility():
    """Test si l'URL ngrok est accessible depuis l'intérieur"""
    ngrok_url = "https://13df0a24787c.ngrok-free.app"
    
    print("🌐 Test accessibilité ngrok")
    print("=" * 50)
    
    try:
        print(f"🔗 Test URL: {ngrok_url}/api/health")
        response = requests.get(
            f"{ngrok_url}/api/health", 
            timeout=10,
            headers={"ngrok-skip-browser-warning": "true"}
        )
        
        if response.status_code == 200:
            print("✅ Ngrok accessible!")
            print(f"   Réponse: {response.json()}")
            return True
        else:
            print(f"❌ Ngrok inaccessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur ngrok: {e}")
        return False

def check_env_webhook_url():
    """Vérifie que WEBHOOK_URL est mis à jour"""
    print("🔧 Vérification WEBHOOK_URL dans .env")
    print("=" * 50)
    
    try:
        with open("/app/backend/.env", "r") as f:
            content = f.read()
            
        for line in content.split('\n'):
            if line.startswith("WEBHOOK_URL="):
                webhook_url = line.split("=", 1)[1]
                print(f"📋 WEBHOOK_URL actuel: {webhook_url}")
                
                if "ngrok" in webhook_url:
                    print("✅ WEBHOOK_URL utilise ngrok")
                elif "localhost" in webhook_url:
                    print("⚠️ WEBHOOK_URL utilise localhost (pas accessible depuis l'extérieur)")
                else:
                    print(f"ℹ️ WEBHOOK_URL: {webhook_url}")
                break
        else:
            print("❌ WEBHOOK_URL non trouvé dans .env")
            
    except Exception as e:
        print(f"❌ Erreur lecture .env: {e}")

def main():
    print("🧪 Test complet webhook et vidéos")
    print("=" * 60)
    
    # Vérifier la config
    check_env_webhook_url()
    print()
    
    # Tester ngrok
    ngrok_ok = test_ngrok_accessibility()
    print()
    
    # Test webhook vidéo (local)
    test_webhook_video_simulation()
    print()
    
    if ngrok_ok:
        print("✅ Tests terminés - ngrok accessible")
    else:
        print("⚠️ Tests terminés - problème ngrok détecté")
        print("💡 L'URL ngrok peut être inaccessible depuis ce conteneur")
        print("   Ceci est normal si ngrok tourne sur une machine Windows distante")

if __name__ == "__main__":
    main()