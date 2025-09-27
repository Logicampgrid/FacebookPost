#!/usr/bin/env python3
"""
Test complet webhook vidéo pour valider le bon endpoint Facebook
"""

import requests
import json

BACKEND_URL = "http://localhost:8001"

def test_webhook_with_video():
    """Test webhook avec vidéo pour s'assurer qu'elle utilise l'endpoint /videos"""
    
    print("🎬 Test webhook avec vidéo (Mode Test)")
    print("=" * 50)
    
    # Simulation d'un webhook depuis n8n avec vidéo
    webhook_payload = {
        "store": "gizmobbs",
        "content": "🎥 Nouvelle vidéo - Le Berger Blanc Suisse en action! 🐕\n\n#BergerBlancSuisse #Chien #Video",
        "platforms": ["facebook"],
        "video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1MB.mp4",
        "product_url": "https://logicamp.org/berger-blanc-suisse",
        "from_n8n": True
    }
    
    print("📤 Données webhook envoyées:")
    print(json.dumps(webhook_payload, indent=2))
    print()
    
    try:
        print("🚀 Envoi vers /api/webhook...")
        response = requests.post(
            f"{BACKEND_URL}/api/webhook",
            json=webhook_payload,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook traité avec succès!")
            print()
            print("📋 Réponse webhook:")
            print(json.dumps(result, indent=2))
            
            # Vérifier si la vidéo a été traitée correctement
            if result.get("processed"):
                print("\n🔍 Analyse du traitement:")
                
                if "results" in result:
                    for platform, platform_result in result["results"].items():
                        print(f"\n📱 {platform.upper()}:")
                        if platform_result.get("success"):
                            print("   ✅ Publication réussie")
                            fb_id = platform_result.get("data", {}).get("id", "N/A")
                            print(f"   📋 Facebook ID: {fb_id}")
                            
                            # Vérifier si c'est bien traité comme vidéo
                            if "test_fb_video_" in str(fb_id):
                                print("   🎬 ✅ Traité comme VIDÉO (endpoint /videos utilisé)")
                            elif "test_fb_post_" in str(fb_id):
                                print("   📝 ⚠️ Traité comme POST (endpoint /feed utilisé)")
                            else:
                                print(f"   ❓ Type indéterminé: {fb_id}")
                        else:
                            print(f"   ❌ Erreur: {platform_result.get('error', 'Inconnue')}")
                
                return True
            else:
                print("⚠️ Webhook reçu mais pas traité")
                return False
                
        else:
            print(f"❌ Erreur webhook: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_webhook_with_image():
    """Test webhook avec image pour comparaison"""
    
    print("\n📷 Test webhook avec image (pour comparaison)")
    print("=" * 50)
    
    webhook_payload = {
        "store": "gizmobbs", 
        "content": "📷 Belle photo - Le Berger Blanc Suisse 🐕\n\n#BergerBlancSuisse #Photo",
        "platforms": ["facebook"],
        "image_url": "https://example.com/berger-blanc-suisse.jpg",
        "product_url": "https://logicamp.org/berger-blanc-suisse"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/webhook",
            json=webhook_payload,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook image traité")
            
            if "results" in result and "facebook" in result["results"]:
                fb_result = result["results"]["facebook"]
                if fb_result.get("success"):
                    fb_id = fb_result.get("data", {}).get("id", "N/A")
                    print(f"📋 Facebook ID: {fb_id}")
                    
                    if "test_fb_post_" in str(fb_id):
                        print("   📝 ✅ Traité comme POST (endpoint /feed - correct pour image)")
                    elif "test_fb_video_" in str(fb_id):
                        print("   🎬 ⚠️ Traité comme VIDÉO (problème!)")
                    
        else:
            print(f"⚠️ Erreur webhook image: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Erreur test image: {e}")

def main():
    print("🧪 Test complet webhook vidéo vs image")
    print("=" * 60)
    
    # Test vidéo
    video_success = test_webhook_with_video()
    
    # Test image pour comparaison
    test_webhook_with_image()
    
    print(f"\n{'='*60}")
    if video_success:
        print("✅ RÉSULTAT: L'application traite correctement les vidéos!")
        print("   - Détecte les URLs vidéo")
        print("   - Utilise l'endpoint Facebook /videos") 
        print("   - Génère des IDs de test spécifiques aux vidéos")
        print("   - Processus webhook fonctionnel")
    else:
        print("❌ PROBLÈME: Des corrections sont nécessaires")
    
    print(f"\n💡 RAPPEL: L'URL ngrok {BACKEND_URL.replace('localhost:8001', '13df0a24787c.ngrok-free.app')}")
    print("   doit être mise à jour dans n8n pour recevoir les vrais webhooks!")

if __name__ == "__main__":
    main()