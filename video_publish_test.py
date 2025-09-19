#!/usr/bin/env python3
"""
Test complet pour la publication vidéo - Correction "method not allowed"
Teste les endpoints vidéo et la publication sur les stores configurés
"""

import requests
import sys
import json
import time
from datetime import datetime

class VideoPublishTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        # Headers pour ngrok si nécessaire
        self.headers = {
            'ngrok-skip-browser-warning': 'true',
            'User-Agent': 'VideoPublishTester/1.0'
        }

    def log_test(self, name, success, details=""):
        """Log un résultat de test"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
        
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details
        })

    def test_health_check(self):
        """Test de santé de l'API"""
        try:
            response = requests.get(f"{self.base_url}/api/health", headers=self.headers, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f" - {data.get('status', 'unknown')}"
            self.log_test("API Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("API Health Check", False, f"Erreur: {str(e)}")
            return False

    def test_video_post_creation(self):
        """Test création d'un post vidéo"""
        try:
            # Données de test pour un post vidéo
            post_data = {
                "user_id": "test_user_video",
                "content": "Test vidéo publication - Le Berger Blanc Suisse 🎬",
                "video_url": "https://example.com/test-video.mp4",
                "video_id": "test_video_123",
                "target_type": "page",
                "target_id": "102401876209415",  # Le Berger Blanc Suisse
                "target_name": "Le Berger Blanc Suisse",
                "platform": "facebook",
                "business_manager_id": "test_bm",
                "business_manager_name": "Test Business Manager",
                "video_metadata": json.dumps({
                    "title": "Test Vidéo",
                    "description": "Description de test",
                    "hashtags": "#test #video #berger"
                })
            }

            response = requests.post(
                f"{self.base_url}/api/posts/video",
                data=post_data,
                headers=self.headers,
                timeout=30
            )
            
            success = response.status_code in [200, 201]  # Accept both 200 and 201
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                post_id = data.get('post', {}).get('id')
                details += f" - Post ID: {post_id}"
                # Stocker l'ID pour les tests suivants
                self.test_post_id = post_id
            else:
                try:
                    error_data = response.json()
                    details += f" - Erreur: {error_data}"
                except:
                    details += f" - Réponse: {response.text[:200]}"

            self.log_test("Création Post Vidéo", success, details)
            return success
            
        except Exception as e:
            self.log_test("Création Post Vidéo", False, f"Erreur: {str(e)}")
            return False

    def test_video_publish_gizmobbs(self):
        """Test publication vidéo sur Le Berger Blanc Suisse (gizmobbs)"""
        if not hasattr(self, 'test_post_id'):
            self.log_test("Publication Vidéo - Le Berger Blanc Suisse", False, "Pas de post ID disponible")
            return False
            
        try:
            response = requests.post(
                f"{self.base_url}/api/posts/{self.test_post_id}/publish",
                headers=self.headers,
                timeout=60  # Timeout plus long pour la publication
            )
            
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f" - Succès: {data.get('success', False)}"
                if data.get('publication_results'):
                    pub_results = data['publication_results']
                    details += f" - Facebook: {pub_results.get('facebook_result', {}).get('test_mode', 'N/A')}"
                    details += f" - Instagram: {pub_results.get('instagram_result', {}).get('test_mode', 'N/A')}"
            else:
                try:
                    error_data = response.json()
                    details += f" - Erreur: {error_data}"
                except:
                    details += f" - Réponse: {response.text[:200]}"

            self.log_test("Publication Vidéo - Le Berger Blanc Suisse", success, details)
            return success
            
        except Exception as e:
            self.log_test("Publication Vidéo - Le Berger Blanc Suisse", False, f"Erreur: {str(e)}")
            return False

    def test_video_post_logicamp(self):
        """Test création et publication pour @logicamp_berger"""
        try:
            # Créer un post pour logicamp
            post_data = {
                "user_id": "test_user_logicamp",
                "content": "Test vidéo @logicamp_berger 🐕",
                "video_url": "https://example.com/logicamp-video.mp4",
                "video_id": "test_video_logicamp",
                "target_type": "page",
                "target_id": "102401876209415",  # Utiliser le même ID pour le test
                "target_name": "@logicamp_berger",
                "platform": "instagram",
                "business_manager_id": "test_bm",
                "business_manager_name": "Test Business Manager",
                "video_metadata": json.dumps({
                    "title": "Test @logicamp_berger",
                    "description": "Test publication Instagram",
                    "hashtags": "#logicamp #berger #test"
                })
            }

            # Créer le post
            create_response = requests.post(
                f"{self.base_url}/api/posts/video",
                data=post_data,
                timeout=30
            )
            
            if create_response.status_code not in [200, 201]:
                self.log_test("Publication @logicamp_berger", False, f"Échec création: {create_response.status_code}")
                return False
            
            post_data = create_response.json()
            logicamp_post_id = post_data.get('post', {}).get('id')
            
            # Publier le post
            publish_response = requests.post(
                f"{self.base_url}/api/posts/{logicamp_post_id}/publish",
                timeout=60
            )
            
            success = publish_response.status_code == 200
            details = f"Status: {publish_response.status_code}"
            
            if success:
                data = publish_response.json()
                details += f" - Succès: {data.get('success', False)}"
                details += f" - Mode test: {data.get('test_mode', False)}"
            else:
                try:
                    error_data = publish_response.json()
                    details += f" - Erreur: {error_data}"
                except:
                    details += f" - Réponse: {publish_response.text[:200]}"

            self.log_test("Publication @logicamp_berger", success, details)
            return success
            
        except Exception as e:
            self.log_test("Publication @logicamp_berger", False, f"Erreur: {str(e)}")
            return False

    def test_cross_platform_video(self):
        """Test publication vidéo croisée (Facebook + Instagram)"""
        try:
            # Créer un post croisé
            post_data = {
                "user_id": "test_user_cross",
                "content": "Test publication croisée vidéo 🎬📱",
                "video_url": "https://example.com/cross-video.mp4",
                "video_id": "test_video_cross",
                "target_type": "cross-post-video",
                "target_id": "cross-post-video",
                "target_name": "Publication vidéo croisée (2 plateformes)",
                "platform": "meta",
                "business_manager_id": "test_bm",
                "business_manager_name": "Test Business Manager",
                "cross_post_targets": json.dumps([
                    {
                        "id": "102401876209415",
                        "name": "Le Berger Blanc Suisse",
                        "platform": "facebook",
                        "type": "page"
                    },
                    {
                        "id": "102401876209415",
                        "name": "@logicamp_berger",
                        "platform": "instagram",
                        "type": "instagram"
                    }
                ]),
                "video_metadata": json.dumps({
                    "title": "Test Croisé",
                    "description": "Publication sur Facebook et Instagram",
                    "hashtags": "#cross #platform #test"
                })
            }

            # Créer le post
            create_response = requests.post(
                f"{self.base_url}/api/posts/video",
                data=post_data,
                timeout=30
            )
            
            if create_response.status_code not in [200, 201]:
                self.log_test("Publication Croisée Vidéo", False, f"Échec création: {create_response.status_code}")
                return False
            
            post_data = create_response.json()
            cross_post_id = post_data.get('post', {}).get('id')
            
            # Publier le post
            publish_response = requests.post(
                f"{self.base_url}/api/posts/{cross_post_id}/publish",
                timeout=90  # Timeout plus long pour publication croisée
            )
            
            success = publish_response.status_code == 200
            details = f"Status: {publish_response.status_code}"
            
            if success:
                data = publish_response.json()
                details += f" - Succès: {data.get('success', False)}"
                if data.get('publication_results'):
                    pub_results = data['publication_results']
                    fb_result = pub_results.get('facebook_result', {})
                    ig_result = pub_results.get('instagram_result', {})
                    details += f" - FB: {'✅' if fb_result.get('test_mode') else '❌'}"
                    details += f" - IG: {'✅' if ig_result.get('test_mode') else '❌'}"
            else:
                try:
                    error_data = publish_response.json()
                    details += f" - Erreur: {error_data}"
                except:
                    details += f" - Réponse: {publish_response.text[:200]}"

            self.log_test("Publication Croisée Vidéo", success, details)
            return success
            
        except Exception as e:
            self.log_test("Publication Croisée Vidéo", False, f"Erreur: {str(e)}")
            return False

    def test_method_not_allowed_fix(self):
        """Test spécifique pour vérifier que l'erreur 'method not allowed' est corrigée"""
        try:
            # Créer un post vidéo simple
            post_data = {
                "user_id": "test_method_fix",
                "content": "Test correction method not allowed",
                "video_url": "https://example.com/method-test.mp4",
                "video_id": "test_method_video",
                "target_type": "page",
                "target_id": "102401876209415",
                "target_name": "Le Berger Blanc Suisse",
                "platform": "facebook",
                "video_metadata": json.dumps({
                    "title": "Test Method Fix",
                    "description": "Vérification correction erreur",
                    "hashtags": "#fix #test"
                })
            }

            create_response = requests.post(
                f"{self.base_url}/api/posts/video",
                data=post_data,
                timeout=30
            )
            
            if create_response.status_code != 201:
                self.log_test("Fix Method Not Allowed", False, f"Échec création: {create_response.status_code}")
                return False
            
            post_data = create_response.json()
            test_post_id = post_data.get('post', {}).get('id')
            
            # Tenter la publication - ne devrait plus retourner 405
            publish_response = requests.post(
                f"{self.base_url}/api/posts/{test_post_id}/publish",
                timeout=60
            )
            
            # Vérifier que ce n'est PAS une erreur 405
            method_not_allowed = publish_response.status_code == 405
            success = not method_not_allowed and publish_response.status_code in [200, 201]
            
            details = f"Status: {publish_response.status_code}"
            if method_not_allowed:
                details += " - ❌ ERREUR 405 ENCORE PRÉSENTE!"
            elif success:
                details += " - ✅ Erreur 405 corrigée"
            else:
                details += f" - Autre erreur: {publish_response.text[:100]}"

            self.log_test("Fix Method Not Allowed", success, details)
            return success
            
        except Exception as e:
            self.log_test("Fix Method Not Allowed", False, f"Erreur: {str(e)}")
            return False

    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🎬 === TEST PUBLICATION VIDÉO - CORRECTION METHOD NOT ALLOWED ===")
        print(f"🌐 URL Backend: {self.base_url}")
        print(f"⏰ Début des tests: {datetime.now().strftime('%H:%M:%S')}")
        print()

        # Tests dans l'ordre logique
        tests = [
            self.test_health_check,
            self.test_video_post_creation,
            self.test_method_not_allowed_fix,
            self.test_video_publish_gizmobbs,
            self.test_video_post_logicamp,
            self.test_cross_platform_video
        ]

        for test in tests:
            try:
                test()
                time.sleep(1)  # Pause entre les tests
            except Exception as e:
                print(f"❌ Erreur inattendue dans {test.__name__}: {str(e)}")
                self.tests_run += 1

        # Résumé final
        print()
        print("=" * 60)
        print(f"📊 RÉSULTATS FINAUX: {self.tests_passed}/{self.tests_run} tests réussis")
        
        if self.tests_passed == self.tests_run:
            print("🎉 TOUS LES TESTS SONT PASSÉS!")
            print("✅ L'erreur 'method not allowed' semble corrigée")
        else:
            print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
            failed_tests = [r for r in self.test_results if not r['success']]
            print(f"❌ Tests échoués: {len(failed_tests)}")
            for test in failed_tests:
                print(f"   - {test['name']}: {test['details']}")

        print()
        print("🔍 POINTS CLÉS À VÉRIFIER:")
        print("   1. L'endpoint /api/posts/{id}/publish accepte les requêtes POST")
        print("   2. La détection des posts vidéo fonctionne correctement")
        print("   3. La publication sur 'Le Berger Blanc Suisse' et '@logicamp_berger'")
        print("   4. Le mode test est activé (pas de vraies publications)")
        
        return self.tests_passed == self.tests_run

def main():
    tester = VideoPublishTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())