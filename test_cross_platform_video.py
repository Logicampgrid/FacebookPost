#!/usr/bin/env python3
"""
Test de la publication vidéo croisée (Facebook + Instagram)
"""
import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8001"
TEST_USER_ID = "test_user_cross_video"

def log_test(message, level="INFO"):
    """Logging pour les tests"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [CROSS-TEST] {message}")

def test_cross_platform_video_publication():
    """Test de publication vidéo croisée Facebook + Instagram"""
    try:
        log_test("Test de publication vidéo croisée...", "TEST")
        
        # Données du post vidéo croisé
        cross_targets = [
            {
                "id": "102401876209415",
                "name": "Le Berger Blanc Suisse",
                "platform": "facebook",
                "type": "page"
            },
            {
                "id": "17841459952999804",
                "name": "@logicamp_berger",
                "platform": "instagram",
                "type": "instagram"
            }
        ]
        
        post_data = {
            "user_id": TEST_USER_ID,
            "content": "Test publication croisée vidéo 🎬\n\nNouvelle vidéo sur Le Berger Blanc Suisse et @logicamp_berger !\n\n#bergerblanc #logicamp #test",
            "video_url": "https://example.com/test-cross-video.mp4",
            "video_id": "test_cross_video_456",
            "target_type": "cross-post-video",
            "target_id": "cross-post-video",
            "target_name": f"Publication vidéo croisée ({len(cross_targets)} plateformes)",
            "platform": "meta",
            "cross_post_targets": json.dumps(cross_targets),
            "business_manager_id": "test_bm_cross",
            "business_manager_name": "Test Cross Business Manager",
            "video_metadata": json.dumps({
                "title": "Test Vidéo Croisée",
                "description": "Test de publication sur Facebook et Instagram simultanément",
                "hashtags": "#bergerblanc #logicamp #test #publication"
            })
        }
        
        log_test("Création du post vidéo croisé...", "INFO")
        
        # Création du post
        response = requests.post(
            f"{API_BASE}/api/posts/video",
            data=post_data,
            timeout=30
        )
        
        if response.status_code != 200:
            log_test(f"❌ Erreur création post croisé: {response.status_code} - {response.text[:200]}", "ERROR")
            return False
        
        result = response.json()
        if not result.get("success"):
            log_test(f"❌ Échec création post croisé: {result.get('message')}", "ERROR")
            return False
        
        post_id = result["post"]["id"]
        log_test(f"✅ Post vidéo croisé créé: {post_id}", "SUCCESS")
        
        # Attendre un peu
        time.sleep(2)
        
        # Publication du post croisé
        log_test("Publication du post vidéo croisé...", "INFO")
        
        pub_response = requests.post(
            f"{API_BASE}/api/posts/{post_id}/publish",
            timeout=60
        )
        
        if pub_response.status_code != 200:
            log_test(f"❌ Erreur publication croisée: {pub_response.status_code} - {pub_response.text[:200]}", "ERROR")
            return False
        
        pub_result = pub_response.json()
        log_test(f"Résultat publication croisée:", "INFO")
        log_test(json.dumps(pub_result, indent=2), "INFO")
        
        if pub_result.get("success"):
            log_test("✅ Publication vidéo croisée réussie!", "SUCCESS")
            
            # Analyser les résultats par plateforme
            pub_data = pub_result.get("publication_results", {})
            if isinstance(pub_data, dict) and pub_data.get("publication_results"):
                for platform_result in pub_data["publication_results"]:
                    target_name = platform_result.get("target")
                    platform = platform_result.get("platform")
                    success = platform_result.get("result", {}).get("success", False)
                    
                    if success:
                        log_test(f"✅ {target_name} ({platform}): Publication réussie", "SUCCESS")
                    else:
                        log_test(f"❌ {target_name} ({platform}): Publication échouée", "ERROR")
            
            return True
        else:
            log_test(f"❌ Échec publication croisée: {pub_result.get('message')}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"❌ Erreur test publication croisée: {str(e)}", "ERROR")
        return False

def main():
    """Fonction principale de test"""
    log_test("=== TEST PUBLICATION VIDÉO CROISÉE ===", "INFO")
    log_test("Test de publication simultanée sur Facebook et Instagram", "INFO")
    
    success = test_cross_platform_video_publication()
    
    log_test("=== RÉSUMÉ TEST CROISÉ ===", "INFO")
    if success:
        log_test("🎉 Publication vidéo croisée fonctionne!", "SUCCESS")
        log_test("✅ Facebook et Instagram supportés", "SUCCESS")
        log_test("✅ @logicamp_berger peut recevoir des vidéos", "SUCCESS")
    else:
        log_test("❌ Problème avec la publication croisée", "ERROR")

if __name__ == "__main__":
    main()