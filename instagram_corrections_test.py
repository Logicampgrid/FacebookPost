#!/usr/bin/env python3
"""
Test des corrections Instagram dans server.py
Teste spécifiquement les corrections apportées au système Instagram
Focus: logicampoutdoor mapping, paramètres conteneur Instagram améliorés, messages d'erreur explicites
"""

import requests
import sys
import json
import os
from datetime import datetime
import tempfile
from PIL import Image
import io

class InstagramCorrectionsTester:
    def __init__(self, base_url="https://fb-webhook-local.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = f"{status} - {name}"
        if details:
            result += f": {details}"
        
        print(result)
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        return success

    def create_test_image(self):
        """Create a test image file"""
        try:
            # Create a simple test image
            img = Image.new('RGB', (800, 600), color='red')
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(temp_file.name, 'JPEG', quality=85)
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            print(f"❌ Erreur création image test: {str(e)}")
            return None

    def create_test_video(self):
        """Create a fake test video file"""
        try:
            # Create a fake MP4 file with proper header
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            # Write a minimal MP4 header
            mp4_header = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom\x00\x00\x00\x08free'
            temp_file.write(mp4_header)
            temp_file.write(b'fake video content for testing' * 100)  # Make it bigger
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            print(f"❌ Erreur création vidéo test: {str(e)}")
            return None

    def test_webhook_endpoint_basic(self):
        """Test basic webhook endpoint accessibility"""
        try:
            url = f"{self.base_url}/api/webhook"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return self.log_test("Webhook endpoint accessible", True, f"Status: {response.status_code}")
            else:
                return self.log_test("Webhook endpoint accessible", False, f"Status: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Webhook endpoint accessible", False, f"Error: {str(e)}")

    def test_logicampoutdoor_mapping(self):
        """Test spécifique pour le store 'logicampoutdoor' qui n'était pas mappé"""
        try:
            url = f"{self.base_url}/api/webhook"
            
            # Create test data for logicampoutdoor
            json_data = {
                "store": "logicampoutdoor",
                "title": "Test LogicampOutdoor Mapping",
                "description": "Test du mapping du store logicampoutdoor qui était manquant",
                "url": "https://example.com/logicampoutdoor-test"
            }
            
            test_image_path = self.create_test_image()
            if not test_image_path:
                return self.log_test("LogicampOutdoor mapping", False, "Failed to create test image")
            
            try:
                files = {
                    'json_data': (None, json.dumps(json_data)),
                    'image': ('logicampoutdoor_test.jpg', open(test_image_path, 'rb'), 'image/jpeg')
                }
                
                print(f"🔍 Testing logicampoutdoor store mapping (previously missing)")
                response = requests.post(url, files=files, timeout=30)
                
                files['image'][1].close()
                os.unlink(test_image_path)
                
                print(f"📥 Response status: {response.status_code}")
                print(f"📄 Response preview: {response.text[:300]}...")
                
                response_text = response.text.lower()
                
                # Check if store is now recognized (no "Invalid store" error)
                if "invalid store" in response_text:
                    return self.log_test("LogicampOutdoor mapping", False, "Store still not recognized - 'Invalid store' error")
                elif response.status_code == 500:
                    return self.log_test("LogicampOutdoor mapping", False, f"Server error 500: {response.text[:200]}")
                elif response.status_code in [200, 201, 202]:
                    return self.log_test("LogicampOutdoor mapping", True, f"Store recognized and processed, status: {response.status_code}")
                elif response.status_code == 400:
                    # Check if it's a meaningful error (auth/token) rather than "invalid store"
                    if any(keyword in response_text for keyword in ["token", "auth", "permission", "access"]):
                        return self.log_test("LogicampOutdoor mapping", True, f"Store recognized, auth error expected: {response.status_code}")
                    else:
                        return self.log_test("LogicampOutdoor mapping", False, f"Bad request: {response.text[:200]}")
                else:
                    return self.log_test("LogicampOutdoor mapping", False, f"Unexpected status: {response.status_code}")
                        
            except Exception as req_error:
                if test_image_path and os.path.exists(test_image_path):
                    os.unlink(test_image_path)
                return self.log_test("LogicampOutdoor mapping", False, f"Request error: {str(req_error)}")
                
        except Exception as e:
            return self.log_test("LogicampOutdoor mapping", False, f"General error: {str(e)}")

    def test_all_store_mappings(self):
        """Test all stores mentioned in the request"""
        stores_to_test = ["gizmobbs", "logicantiq", "outdoor", "logicampoutdoor"]
        all_success = True
        
        for store in stores_to_test:
            try:
                url = f"{self.base_url}/api/webhook"
                
                json_data = {
                    "store": store,
                    "title": f"Test Store {store}",
                    "description": f"Test mapping pour le store {store}",
                    "url": f"https://example.com/{store}-test"
                }
                
                test_image_path = self.create_test_image()
                if not test_image_path:
                    self.log_test(f"Store mapping - {store}", False, "Failed to create test image")
                    all_success = False
                    continue
                
                try:
                    files = {
                        'json_data': (None, json.dumps(json_data)),
                        'image': (f'{store}_test.jpg', open(test_image_path, 'rb'), 'image/jpeg')
                    }
                    
                    print(f"🏪 Testing store: {store}")
                    response = requests.post(url, files=files, timeout=30)
                    
                    files['image'][1].close()
                    os.unlink(test_image_path)
                    
                    response_text = response.text.lower()
                    
                    if "invalid store" in response_text:
                        self.log_test(f"Store mapping - {store}", False, "Store not recognized")
                        all_success = False
                    elif response.status_code == 500:
                        self.log_test(f"Store mapping - {store}", False, f"Server error: {response.text[:100]}")
                        all_success = False
                    elif response.status_code in [200, 201, 202, 400]:
                        # 400 is OK if it's auth-related, not store-related
                        if response.status_code == 400 and "invalid store" not in response_text:
                            self.log_test(f"Store mapping - {store}", True, f"Store recognized, auth error expected")
                        else:
                            self.log_test(f"Store mapping - {store}", True, f"Store processed: {response.status_code}")
                    else:
                        self.log_test(f"Store mapping - {store}", False, f"Unexpected status: {response.status_code}")
                        all_success = False
                            
                except Exception as req_error:
                    if test_image_path and os.path.exists(test_image_path):
                        os.unlink(test_image_path)
                    self.log_test(f"Store mapping - {store}", False, f"Request error: {str(req_error)}")
                    all_success = False
                    
            except Exception as e:
                self.log_test(f"Store mapping - {store}", False, f"General error: {str(e)}")
                all_success = False
        
        return all_success

    def test_improved_instagram_video_parameters(self):
        """Test improved Instagram container parameters for videos"""
        try:
            url = f"{self.base_url}/api/webhook"
            
            json_data = {
                "store": "logicampoutdoor",
                "title": "Test Paramètres Vidéo Instagram Améliorés",
                "description": "Test des paramètres de conteneur Instagram améliorés pour les vidéos",
                "url": "https://example.com/video-instagram-test"
            }
            
            test_video_path = self.create_test_video()
            if not test_video_path:
                return self.log_test("Instagram video parameters", False, "Failed to create test video")
            
            try:
                files = {
                    'json_data': (None, json.dumps(json_data)),
                    'video': ('instagram_test.mp4', open(test_video_path, 'rb'), 'video/mp4')
                }
                
                print(f"🎬 Testing improved Instagram video parameters")
                response = requests.post(url, files=files, timeout=60)  # Longer timeout for video
                
                files['video'][1].close()
                os.unlink(test_video_path)
                
                print(f"📥 Video response status: {response.status_code}")
                print(f"📄 Video response preview: {response.text[:300]}...")
                
                # Check if video processing doesn't crash the server
                if response.status_code == 500:
                    # Check if it's a specific Instagram container error
                    response_text = response.text.lower()
                    if "failed to create media container" in response_text:
                        return self.log_test("Instagram video parameters", False, "Instagram container creation still failing")
                    else:
                        return self.log_test("Instagram video parameters", False, f"Server crash on video: {response.text[:200]}")
                elif response.status_code in [200, 201, 202]:
                    return self.log_test("Instagram video parameters", True, f"Video processed successfully: {response.status_code}")
                elif response.status_code == 400:
                    # Check if it's auth-related rather than video parameter issue
                    response_text = response.text.lower()
                    if any(keyword in response_text for keyword in ["token", "auth", "permission"]):
                        return self.log_test("Instagram video parameters", True, "Video parameters OK, auth error expected")
                    else:
                        return self.log_test("Instagram video parameters", False, f"Video parameter issue: {response.text[:200]}")
                else:
                    return self.log_test("Instagram video parameters", False, f"Unexpected status: {response.status_code}")
                    
            except Exception as req_error:
                if test_video_path and os.path.exists(test_video_path):
                    os.unlink(test_video_path)
                return self.log_test("Instagram video parameters", False, f"Request error: {str(req_error)}")
                
        except Exception as e:
            return self.log_test("Instagram video parameters", False, f"General error: {str(e)}")

    def test_explicit_error_messages(self):
        """Test that error messages are more explicit"""
        try:
            url = f"{self.base_url}/api/webhook"
            
            # Test with invalid store to check error message clarity
            json_data = {
                "store": "invalid_store_name_xyz123",
                "title": "Test Messages d'Erreur Explicites",
                "description": "Test que les messages d'erreur sont plus explicites",
                "url": "https://example.com/error-test"
            }
            
            test_image_path = self.create_test_image()
            if not test_image_path:
                return self.log_test("Explicit error messages", False, "Failed to create test image")
            
            try:
                files = {
                    'json_data': (None, json.dumps(json_data)),
                    'image': ('error_test.jpg', open(test_image_path, 'rb'), 'image/jpeg')
                }
                
                print(f"🔍 Testing explicit error messages with invalid store")
                response = requests.post(url, files=files, timeout=30)
                
                files['image'][1].close()
                os.unlink(test_image_path)
                
                print(f"📥 Error test response status: {response.status_code}")
                print(f"📄 Error test response: {response.text[:300]}...")
                
                # Check if error message is clear and explicit
                if response.status_code == 500:
                    return self.log_test("Explicit error messages", False, f"Server crash instead of clear error: {response.text[:200]}")
                elif response.status_code == 400:
                    response_text = response.text.lower()
                    if "invalid store" in response_text or "store" in response_text:
                        # Check if the error message is detailed enough
                        if len(response.text) > 20:  # Not just a generic error
                            return self.log_test("Explicit error messages", True, f"Clear and detailed error: {response.text[:200]}")
                        else:
                            return self.log_test("Explicit error messages", False, f"Error too generic: {response.text}")
                    else:
                        return self.log_test("Explicit error messages", False, f"Unclear error message: {response.text[:200]}")
                else:
                    return self.log_test("Explicit error messages", False, f"Unexpected status for invalid store: {response.status_code}")
                    
            except Exception as req_error:
                if test_image_path and os.path.exists(test_image_path):
                    os.unlink(test_image_path)
                return self.log_test("Explicit error messages", False, f"Request error: {str(req_error)}")
                
        except Exception as e:
            return self.log_test("Explicit error messages", False, f"General error: {str(e)}")

    def test_multipart_form_data_handling(self):
        """Test that multipart/form-data is properly handled"""
        try:
            url = f"{self.base_url}/api/webhook"
            
            json_data = {
                "store": "logicampoutdoor",
                "title": "Test Multipart Form-Data",
                "description": "Test du traitement correct des données multipart/form-data",
                "url": "https://example.com/multipart-test"
            }
            
            test_image_path = self.create_test_image()
            if not test_image_path:
                return self.log_test("Multipart form-data handling", False, "Failed to create test image")
            
            try:
                # Test with proper multipart format
                files = {
                    'json_data': (None, json.dumps(json_data)),
                    'image': ('multipart_test.jpg', open(test_image_path, 'rb'), 'image/jpeg')
                }
                
                print(f"📋 Testing multipart/form-data handling")
                response = requests.post(url, files=files, timeout=30)
                
                files['image'][1].close()
                os.unlink(test_image_path)
                
                # Check if the request was processed correctly
                if response.status_code == 400 and "multipart" in response.text.lower():
                    return self.log_test("Multipart form-data handling", False, "Multipart format rejected")
                elif response.status_code == 500:
                    return self.log_test("Multipart form-data handling", False, f"Server crash on multipart: {response.text[:200]}")
                elif response.status_code in [200, 201, 202, 400]:
                    # 400 is OK if it's not multipart-related
                    if response.status_code == 400 and "multipart" not in response.text.lower():
                        return self.log_test("Multipart form-data handling", True, "Multipart processed correctly, other error expected")
                    else:
                        return self.log_test("Multipart form-data handling", True, f"Multipart processed: {response.status_code}")
                else:
                    return self.log_test("Multipart form-data handling", False, f"Unexpected status: {response.status_code}")
                    
            except Exception as req_error:
                if test_image_path and os.path.exists(test_image_path):
                    os.unlink(test_image_path)
                return self.log_test("Multipart form-data handling", False, f"Request error: {str(req_error)}")
                
        except Exception as e:
            return self.log_test("Multipart form-data handling", False, f"General error: {str(e)}")

    def run_all_tests(self):
        """Run all Instagram correction tests"""
        print("🚀 TESTS DES CORRECTIONS INSTAGRAM")
        print("=" * 60)
        print("🎯 Focus: logicampoutdoor mapping, paramètres Instagram vidéo, messages d'erreur")
        print()
        
        # Test 1: Basic webhook accessibility
        self.test_webhook_endpoint_basic()
        
        # Test 2: Specific test for logicampoutdoor (the main fix)
        self.test_logicampoutdoor_mapping()
        
        # Test 3: All store mappings
        self.test_all_store_mappings()
        
        # Test 4: Improved Instagram video parameters
        self.test_improved_instagram_video_parameters()
        
        # Test 5: Explicit error messages
        self.test_explicit_error_messages()
        
        # Test 6: Multipart form-data handling
        self.test_multipart_form_data_handling()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS CORRECTIONS INSTAGRAM")
        print("=" * 60)
        print(f"Tests exécutés: {self.tests_run}")
        print(f"Tests réussis: {self.tests_passed}")
        print(f"Tests échoués: {self.tests_run - self.tests_passed}")
        print(f"Taux de réussite: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Detailed results
        print("\n📋 DÉTAILS DES RÉSULTATS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['name']}")
            if result["details"]:
                print(f"   └─ {result['details']}")
        
        # Specific feedback on corrections
        print("\n🔧 ÉVALUATION DES CORRECTIONS:")
        
        logicampoutdoor_test = next((r for r in self.test_results if "LogicampOutdoor" in r["name"]), None)
        if logicampoutdoor_test:
            if logicampoutdoor_test["success"]:
                print("✅ Correction logicampoutdoor: RÉUSSIE")
            else:
                print("❌ Correction logicampoutdoor: ÉCHOUÉE - Store toujours non reconnu")
        
        video_test = next((r for r in self.test_results if "video parameters" in r["name"]), None)
        if video_test:
            if video_test["success"]:
                print("✅ Paramètres vidéo Instagram: AMÉLIORÉS")
            else:
                print("❌ Paramètres vidéo Instagram: PROBLÈMES PERSISTANTS")
        
        error_test = next((r for r in self.test_results if "error messages" in r["name"]), None)
        if error_test:
            if error_test["success"]:
                print("✅ Messages d'erreur: PLUS EXPLICITES")
            else:
                print("❌ Messages d'erreur: TOUJOURS PEU CLAIRS")
        
        success_rate = (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0
        
        if success_rate >= 80:
            print("\n🎉 CORRECTIONS INSTAGRAM: GLOBALEMENT RÉUSSIES")
        elif success_rate >= 60:
            print("\n⚠️ CORRECTIONS INSTAGRAM: PARTIELLEMENT RÉUSSIES")
        else:
            print("\n❌ CORRECTIONS INSTAGRAM: PROBLÈMES DÉTECTÉS")
        
        return self.tests_passed == self.tests_run

def main():
    print("🔧 Test des corrections Instagram dans server.py")
    print("🎯 Focus: Store mappings, paramètres vidéo Instagram, messages d'erreur")
    print()
    
    tester = InstagramCorrectionsTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 TOUTES LES CORRECTIONS FONCTIONNENT!")
        return 0
    else:
        failed_count = tester.tests_run - tester.tests_passed
        print(f"\n⚠️ {failed_count} CORRECTION(S) À REVOIR")
        return 1

if __name__ == "__main__":
    sys.exit(main())