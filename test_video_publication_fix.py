#!/usr/bin/env python3
"""
Test de la correction de l'erreur "method not allowed" pour la publication vidéo
"""
import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "https://34d34f066475.ngrok-free.app"  # URL ngrok active
TEST_USER_ID = "test_user_video_fix"

def log_test(message, level="INFO"):
    """Logging pour les tests"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [TEST] {message}")

def test_api_health():
    """Test de la santé de l'API"""
    try:
        log_test("Test de la santé de l'API...", "TEST")
        
        response = requests.get(f"{API_BASE}/api/health", timeout=10)
        
        if response.status_code == 200:
            log_test("✅ API disponible", "SUCCESS")
            return True
        else:
            log_test(f"❌ API non disponible: {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"❌ Erreur test API: {str(e)}", "ERROR")
        return False

def test_video_post_creation():
    """Test de création d'un post vidéo"""
    try:
        log_test("Test de création d'un post vidéo...", "TEST")
        
        # Données du post vidéo de test
        post_data = {
            "user_id": TEST_USER_ID,
            "content": "Test vidéo publication Le Berger Blanc Suisse 🎬 #test #bergerblanc",
            "video_url": "https://example.com/test-video.mp4",
            "video_id": "test_video_123",
            "target_type": "page",
            "target_id": "102401876209415",  # Le Berger Blanc Suisse
            "target_name": "Le Berger Blanc Suisse",
            "platform": "facebook",
            "business_manager_id": "test_bm",
            "business_manager_name": "Test Business Manager",
            "video_metadata": json.dumps({
                "title": "Test Vidéo Le Berger Blanc Suisse",
                "description": "Vidéo de test pour vérifier la publication",
                "hashtags": "#test #bergerblanc #publication"
            })
        }
        
        log_test("Envoi de la requête de création de post vidéo...", "INFO")
        
        response = requests.post(
            f"{API_BASE}/api/posts/video",
            data=post_data,
            timeout=30
        )
        
        log_test(f"Réponse création post: {response.status_code}", "INFO")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                post_id = result["post"]["id"]
                log_test(f"✅ Post vidéo créé avec succès: {post_id}", "SUCCESS")
                return post_id
            else:
                log_test(f"❌ Échec création post: {result.get('message', 'Erreur inconnue')}", "ERROR")
                return None
        else:
            log_test(f"❌ Erreur HTTP création post: {response.status_code} - {response.text[:200]}", "ERROR")
            return None
            
    except Exception as e:
        log_test(f"❌ Erreur test création post: {str(e)}", "ERROR")
        return None

def test_video_post_publication(post_id):
    """Test de publication d'un post vidéo"""
    try:
        log_test(f"Test de publication du post vidéo {post_id}...", "TEST")
        
        response = requests.post(
            f"{API_BASE}/api/posts/{post_id}/publish",
            timeout=60  # Timeout plus long pour la publication
        )
        
        log_test(f"Réponse publication: {response.status_code}", "INFO")
        
        if response.status_code == 200:
            result = response.json()
            log_test(f"Résultat publication: {json.dumps(result, indent=2)}", "INFO")
            
            if result.get("success"):
                log_test("✅ Publication vidéo réussie!", "SUCCESS")
                
                # Afficher les détails de publication
                pub_results = result.get("publication_results", {})
                if isinstance(pub_results, dict):
                    if pub_results.get("test_mode"):
                        log_test("🧪 Publication en mode TEST (pas de publication réelle)", "INFO")
                    
                    if pub_results.get("facebook_result"):
                        log_test(f"✅ Facebook: {pub_results['facebook_result'].get('id', 'Publié')}", "SUCCESS")
                    
                    if pub_results.get("instagram_result"):
                        log_test(f"✅ Instagram: {pub_results['instagram_result'].get('id', 'Publié')}", "SUCCESS")
                    
                    if pub_results.get("errors"):
                        for error in pub_results["errors"]:
                            log_test(f"⚠️ Erreur: {error}", "WARNING")
                
                return True
            else:
                log_test(f"❌ Échec publication: {result.get('message', 'Erreur inconnue')}", "ERROR")
                if result.get("publication_results", {}).get("errors"):
                    for error in result["publication_results"]["errors"]:
                        log_test(f"  • {error}", "ERROR")
                return False
        
        elif response.status_code == 405:
            log_test("❌ ERREUR 'Method Not Allowed' - Le problème persiste!", "ERROR")
            log_test(f"Réponse: {response.text}", "ERROR")
            return False
        else:
            log_test(f"❌ Erreur HTTP publication: {response.status_code} - {response.text[:200]}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"❌ Erreur test publication: {str(e)}", "ERROR")
        return False

def main():
    """Fonction principale de test"""
    log_test("=== DÉBUT TEST CORRECTION PUBLICATION VIDÉO ===", "INFO")
    log_test(f"URL API: {API_BASE}", "INFO")
    log_test(f"Mode test activé: TRUE", "INFO")
    
    # Test 1: Santé de l'API
    if not test_api_health():
        log_test("❌ API non disponible, arrêt des tests", "ERROR")
        return
    
    # Test 2: Création du post vidéo
    post_id = test_video_post_creation()
    if not post_id:
        log_test("❌ Impossible de créer le post vidéo, arrêt des tests", "ERROR")
        return
    
    # Attendre un peu avant la publication
    log_test("⏱️ Attente avant publication...", "INFO")
    time.sleep(2)
    
    # Test 3: Publication du post vidéo
    publication_success = test_video_post_publication(post_id)
    
    # Résumé
    log_test("=== RÉSUMÉ DES TESTS ===", "INFO")
    log_test(f"✅ API disponible: OUI", "SUCCESS")
    log_test(f"✅ Création post vidéo: {'OUI' if post_id else 'NON'}", "SUCCESS" if post_id else "ERROR")
    log_test(f"✅ Publication vidéo: {'OUI' if publication_success else 'NON'}", "SUCCESS" if publication_success else "ERROR")
    
    if publication_success:
        log_test("🎉 CORRECTION RÉUSSIE! L'erreur 'method not allowed' est corrigée!", "SUCCESS")
        log_test("🎬 La publication vidéo fonctionne maintenant correctement", "SUCCESS")
    else:
        log_test("❌ CORRECTION INCOMPLÈTE - Il reste des problèmes à résoudre", "ERROR")
    
    log_test("=== FIN TEST CORRECTION PUBLICATION VIDÉO ===", "INFO")

if __name__ == "__main__":
    main()