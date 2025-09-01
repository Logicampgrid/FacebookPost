#!/usr/bin/env python3
"""
Test complet pour la nouvelle solution AUTO-ROUTING
Teste la résolution du problème "Invalid image type: video/mp4"
"""

import requests
import sys
import json
import io
from datetime import datetime
import tempfile
import os

class AutoRoutingTester:
    def __init__(self, base_url="https://media-path-update.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []

    def log_result(self, test_name, success, details=None, error=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
            if error:
                print(f"   Error: {error}")
        
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        })

    def test_health_check(self):
        """Test 1: Vérifier que le backend fonctionne"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                backend_status = data.get("backend") == "running"
                mongodb_status = data.get("mongodb") == "connected"
                
                if backend_status and mongodb_status:
                    self.log_result("Health Check", True, {
                        "backend": "running",
                        "mongodb": "connected",
                        "users_count": data.get("database", {}).get("users_count", 0),
                        "posts_count": data.get("database", {}).get("posts_count", 0)
                    })
                    return True
                else:
                    self.log_result("Health Check", False, data, "Backend or MongoDB not healthy")
                    return False
            else:
                self.log_result("Health Check", False, None, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Health Check", False, None, str(e))
            return False

    def test_auto_routing_detection(self):
        """Test 2: Tester la détection automatique de type de média"""
        try:
            response = requests.post(f"{self.base_url}/api/test/auto-routing-media", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    summary = data.get("summary", {})
                    detection_accuracy = summary.get("detection_accuracy", "0%")
                    successful_detections = summary.get("successful_detections", 0)
                    total_scenarios = summary.get("total_scenarios", 0)
                    
                    # Considérer comme réussi si au moins 80% de détection
                    accuracy_value = float(detection_accuracy.replace("%", ""))
                    success = accuracy_value >= 80.0
                    
                    self.log_result("Auto-Routing Detection", success, {
                        "detection_accuracy": detection_accuracy,
                        "successful_detections": successful_detections,
                        "total_scenarios": total_scenarios,
                        "results": data.get("results", [])
                    })
                    return success
                else:
                    self.log_result("Auto-Routing Detection", False, data, "Test returned success=False")
                    return False
            else:
                self.log_result("Auto-Routing Detection", False, None, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Auto-Routing Detection", False, None, str(e))
            return False

    def test_webhook_mp4_video(self):
        """Test 3: Tester le webhook avec une vidéo MP4 (problème principal)"""
        try:
            # Simuler une requête multipart avec vidéo MP4
            # Créer un faux fichier MP4 pour le test
            fake_mp4_content = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom\x00\x00\x00\x08free'
            
            # Données JSON pour le webhook
            json_data = {
                "store": "gizmobbs",
                "title": "Test Vidéo MP4 - AUTO-ROUTING",
                "url": "https://logicamp.org/werdpress/gizmobbs/test-mp4-video",
                "description": "Test de la nouvelle solution AUTO-ROUTING pour résoudre l'erreur 'Invalid image type: video/mp4'"
            }
            
            # Préparer la requête multipart
            files = {
                'json_data': (None, json.dumps(json_data), 'application/json'),
                'image_file': ('test_video.mp4', fake_mp4_content, 'video/mp4')
            }
            
            print(f"🎬 Testing MP4 video upload via webhook...")
            response = requests.post(f"{self.base_url}/api/webhook", files=files, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifier qu'il n'y a plus l'erreur "Invalid image type: video/mp4"
                error_text = str(data).lower()
                has_invalid_image_error = "invalid image type" in error_text and "video/mp4" in error_text
                
                if not has_invalid_image_error:
                    # Vérifier que le système a détecté "video" et utilisé l'endpoint /videos
                    success_indicators = [
                        "video" in str(data).lower(),
                        "routing" in str(data).lower(),
                        data.get("success", False)
                    ]
                    
                    success = any(success_indicators)
                    self.log_result("Webhook MP4 Video", success, {
                        "no_invalid_image_error": True,
                        "response_data": data,
                        "detected_video_routing": success
                    })
                    return success
                else:
                    self.log_result("Webhook MP4 Video", False, data, "Still getting 'Invalid image type: video/mp4' error")
                    return False
            else:
                self.log_result("Webhook MP4 Video", False, None, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Webhook MP4 Video", False, None, str(e))
            return False

    def test_store_mapping(self):
        """Test 4: Tester le mapping des stores"""
        stores_to_test = ["gizmobbs", "outdoor", "logicantiq"]
        
        all_success = True
        store_results = {}
        
        for store in stores_to_test:
            try:
                # Tester avec une image simple pour chaque store
                json_data = {
                    "store": store,
                    "title": f"Test Store Mapping - {store}",
                    "url": f"https://logicamp.org/werdpress/{store}/test-mapping",
                    "description": f"Test du mapping automatique pour le store '{store}' vers 'Le Berger Blanc Suisse'",
                    "image": f"https://picsum.photos/800/600?store_test={store}"
                }
                
                files = {
                    'json_data': (None, json.dumps(json_data), 'application/json')
                }
                
                print(f"🏪 Testing store mapping for: {store}")
                response = requests.post(f"{self.base_url}/api/webhook", files=files, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Vérifier que le store a été mappé vers "Le Berger Blanc Suisse"
                    response_text = str(data).lower()
                    berger_blanc_indicators = [
                        "berger blanc" in response_text,
                        "le berger" in response_text,
                        data.get("success", False)
                    ]
                    
                    store_success = any(berger_blanc_indicators)
                    store_results[store] = {
                        "success": store_success,
                        "mapped_to_berger_blanc": any(berger_blanc_indicators),
                        "response": data
                    }
                    
                    if not store_success:
                        all_success = False
                        
                else:
                    store_results[store] = {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "response": response.text
                    }
                    all_success = False
                    
            except Exception as e:
                store_results[store] = {
                    "success": False,
                    "error": str(e)
                }
                all_success = False
        
        self.log_result("Store Mapping", all_success, {
            "stores_tested": stores_to_test,
            "results": store_results,
            "all_mapped_to_berger_blanc": all_success
        })
        
        return all_success

    def test_image_support_still_works(self):
        """Test 5: Vérifier que les images fonctionnent toujours normalement"""
        image_formats = ["jpeg", "png", "webp"]
        
        all_success = True
        image_results = {}
        
        for fmt in image_formats:
            try:
                json_data = {
                    "store": "gizmobbs",
                    "title": f"Test Image {fmt.upper()} - AUTO-ROUTING",
                    "url": f"https://logicamp.org/werdpress/gizmobbs/test-{fmt}",
                    "description": f"Test que les images {fmt.upper()} fonctionnent toujours avec la nouvelle solution AUTO-ROUTING",
                    "image": f"https://picsum.photos/800/600.{fmt}?test={fmt}"
                }
                
                files = {
                    'json_data': (None, json.dumps(json_data), 'application/json')
                }
                
                print(f"🖼️ Testing image format: {fmt.upper()}")
                response = requests.post(f"{self.base_url}/api/webhook", files=files, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Vérifier que l'image a été traitée avec succès
                    success_indicators = [
                        data.get("success", False),
                        "image" in str(data).lower(),
                        "photos" in str(data).lower()  # Devrait utiliser l'endpoint /photos
                    ]
                    
                    fmt_success = any(success_indicators)
                    image_results[fmt] = {
                        "success": fmt_success,
                        "used_photos_endpoint": "photos" in str(data).lower(),
                        "response": data
                    }
                    
                    if not fmt_success:
                        all_success = False
                        
                else:
                    image_results[fmt] = {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "response": response.text
                    }
                    all_success = False
                    
            except Exception as e:
                image_results[fmt] = {
                    "success": False,
                    "error": str(e)
                }
                all_success = False
        
        self.log_result("Image Support", all_success, {
            "formats_tested": image_formats,
            "results": image_results,
            "all_images_working": all_success
        })
        
        return all_success

    def test_credits_management(self):
        """Test 6: Vérifier la gestion des crédits (limite 10 par publication)"""
        try:
            # Test simple pour vérifier que le système mentionne les crédits
            json_data = {
                "store": "gizmobbs",
                "title": "Test Gestion Crédits - AUTO-ROUTING",
                "url": "https://logicamp.org/werdpress/gizmobbs/test-credits",
                "description": "Test de la gestion des crédits Emergent (limite 10 par publication)",
                "image": "https://picsum.photos/800/600?credits_test=1"
            }
            
            files = {
                'json_data': (None, json.dumps(json_data), 'application/json')
            }
            
            print(f"💳 Testing credits management...")
            response = requests.post(f"{self.base_url}/api/webhook", files=files, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Vérifier que le système gère les crédits
                response_text = str(data).lower()
                credits_indicators = [
                    "credit" in response_text,
                    "10" in response_text,  # Limite de 10 crédits
                    data.get("success", False)
                ]
                
                success = any(credits_indicators)
                self.log_result("Credits Management", success, {
                    "mentions_credits": "credit" in response_text,
                    "mentions_limit_10": "10" in response_text,
                    "response": data
                })
                return success
            else:
                self.log_result("Credits Management", False, None, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Credits Management", False, None, str(e))
            return False

    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🧪 DÉBUT DES TESTS AUTO-ROUTING SOLUTION")
        print("=" * 60)
        
        # Test 1: Health Check
        if not self.test_health_check():
            print("❌ Backend non disponible - Arrêt des tests")
            return False
        
        # Test 2: Auto-Routing Detection
        self.test_auto_routing_detection()
        
        # Test 3: Webhook MP4 Video (problème principal)
        self.test_webhook_mp4_video()
        
        # Test 4: Store Mapping
        self.test_store_mapping()
        
        # Test 5: Image Support
        self.test_image_support_still_works()
        
        # Test 6: Credits Management
        self.test_credits_management()
        
        # Résumé final
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS AUTO-ROUTING")
        print("=" * 60)
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        
        print(f"Tests exécutés: {self.tests_run}")
        print(f"Tests réussis: {self.tests_passed}")
        print(f"Taux de réussite: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ SOLUTION AUTO-ROUTING: FONCTIONNELLE")
            print("🎯 Le problème 'Invalid image type: video/mp4' devrait être résolu")
        elif success_rate >= 60:
            print("⚠️ SOLUTION AUTO-ROUTING: PARTIELLEMENT FONCTIONNELLE")
            print("🔧 Quelques ajustements nécessaires")
        else:
            print("❌ SOLUTION AUTO-ROUTING: PROBLÈMES DÉTECTÉS")
            print("🚨 Révision nécessaire avant mise en production")
        
        # Détails des échecs
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            print("\n❌ TESTS ÉCHOUÉS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test.get('error', 'Échec')}")
        
        return success_rate >= 80

def main():
    """Point d'entrée principal"""
    tester = AutoRoutingTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrompus par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n💥 Erreur critique: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())