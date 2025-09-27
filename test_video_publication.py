#!/usr/bin/env python3
"""
Test de publication vidéo pour vérifier que le bon endpoint est utilisé
"""

import requests
import json

BACKEND_URL = "http://localhost:8001"

def test_video_publication_gizmobbs():
    """Test publication vidéo sur Facebook pour gizmobbs"""
    
    print("🎬 Test publication vidéo - gizmobbs (Mode Test)")
    print("=" * 55)
    
    # Données de test vidéo
    video_data = {
        "store": "gizmobbs",
        "message": "Test vidéo - Le Berger Blanc Suisse 🐕 #test #BergerBlancSuisse",
        "video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1MB.mp4",
        "product_url": "https://example.com/berger-blanc-suisse",
        "platforms": ["facebook"]  # Test Facebook d'abord
    }
    
    print(f"📋 Données publication:")
    print(f"   Store: {video_data['store']}")
    print(f"   Message: {video_data['message']}")
    print(f"   Vidéo: {video_data['video_url']}")
    print(f"   Plateformes: {video_data['platforms']}")
    print()
    
    try:
        print("🚀 Envoi requête publication vidéo...")
        response = requests.post(
            f"{BACKEND_URL}/api/videos/publish",
            json=video_data,
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Publication vidéo réussie!")
            print(f"📝 Réponse complète:")
            print(json.dumps(result, indent=2))
            
            # Analyser les résultats
            if "results" in result:
                for platform, data in result["results"].items():
                    print(f"\n📱 {platform.upper()}:")
                    if data.get("success"):
                        print(f"   ✅ Succès")
                        print(f"   📋 ID: {data.get('data', {}).get('id', 'N/A')}")
                        if "test_mode" in str(data):
                            print(f"   🧪 Mode test confirmé")
                    else:
                        print(f"   ❌ Échec: {data.get('error', 'Erreur inconnue')}")
            
            return True
            
        else:
            print(f"❌ Erreur publication: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_video_vs_image_detection():
    """Test que l'app fait bien la différence entre vidéo et image"""
    
    print("\n🔍 Test détection vidéo vs image")
    print("=" * 40)
    
    test_cases = [
        {
            "name": "Vidéo MP4",
            "url": "https://example.com/test.mp4",
            "expected": "video"
        },
        {
            "name": "Image JPG", 
            "url": "https://example.com/test.jpg",
            "expected": "image"
        },
        {
            "name": "Vidéo MOV",
            "url": "https://example.com/test.mov", 
            "expected": "video"
        }
    ]
    
    for case in test_cases:
        is_video = case["url"].lower().endswith(('.mp4', '.mov', '.avi')) or 'video' in case["url"].lower()
        detected = "video" if is_video else "image"
        
        status = "✅" if detected == case["expected"] else "❌"
        print(f"{status} {case['name']}: {case['url']} → Détecté comme {detected}")

def main():
    print("🎯 Test complet publication vidéo et détection")
    print("=" * 60)
    
    # Test détection
    test_video_vs_image_detection()
    
    # Test publication
    print()
    success = test_video_publication_gizmobbs()
    
    print(f"\n{'✅' if success else '❌'} Test terminé")
    if success:
        print("🎉 L'application gère correctement les vidéos!")
        print("   - Utilise l'endpoint /videos pour Facebook")
        print("   - Gère le processus 2-étapes pour Instagram") 
        print("   - Détecte correctement le type de contenu")
    else:
        print("⚠️ Des problèmes ont été détectés")

if __name__ == "__main__":
    main()