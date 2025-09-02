#!/usr/bin/env python3
"""
Enhanced Features Test for Meta Publishing Platform
Tests the new enhanced product descriptions and clickable images functionality
"""

import requests
import json
import sys
from datetime import datetime

class EnhancedFeaturesTest:
    def __init__(self, base_url="https://ecu-corrector.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        if success:
            print(f"   Server time: {response.get('timestamp')}")
        return success

    def test_enhanced_product_description_generation(self):
        """Test the enhanced product description generation"""
        print(f"\n🧪 Testing Enhanced Product Description Generation...")
        
        test_cases = [
            {
                "name": "Facebook Platform",
                "data": {
                    "title": "Smartphone Premium 2025",
                    "description": "Le dernier smartphone avec toutes les fonctionnalités avancées",
                    "shop_type": "gizmobbs",
                    "platform": "facebook"
                }
            },
            {
                "name": "Instagram Platform",
                "data": {
                    "title": "Tente de Camping Ultra-Légère",
                    "description": "Parfaite pour vos aventures en montagne",
                    "shop_type": "outdoor", 
                    "platform": "instagram"
                }
            },
            {
                "name": "Antique Product",
                "data": {
                    "title": "Vase en Porcelaine du 18ème",
                    "description": "Magnifique pièce d'époque en parfait état",
                    "shop_type": "logicantiq",
                    "platform": "facebook"
                }
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            success, response = self.run_test(
                f"Enhanced Description ({test_case['name']})",
                "POST",
                "api/test/enhanced-description",
                200,
                data=test_case["data"]
            )
            
            if success:
                enhanced_content = response.get("enhanced_content", "")
                original_content = response.get("original_content", "")
                platform = response.get("platform", "")
                shop_type = response.get("shop_type", "")
                
                print(f"   Platform: {platform}")
                print(f"   Shop Type: {shop_type}")
                print(f"   Original length: {len(original_content)} chars")
                print(f"   Enhanced length: {len(enhanced_content)} chars")
                
                # Check platform-specific enhancements
                if platform == "instagram":
                    if "lien en bio" in enhanced_content.lower():
                        print("✅ Instagram-specific 'Lien en bio' added")
                    else:
                        print("❌ Missing Instagram-specific content")
                        all_passed = False
                        
                    if "#" in enhanced_content:
                        print("✅ Hashtags added for Instagram")
                    else:
                        print("❌ Missing hashtags for Instagram")
                        all_passed = False
                        
                elif platform == "facebook":
                    if len(enhanced_content) > len(original_content):
                        print("✅ Facebook content enhanced")
                    else:
                        print("⚠️  Facebook content not significantly enhanced")
                
                # Check shop-specific content
                if shop_type == "outdoor" and "outdoor" in enhanced_content.lower():
                    print("✅ Outdoor-specific content detected")
                elif shop_type == "gizmobbs" and ("berger" in enhanced_content.lower() or "chien" in enhanced_content.lower()):
                    print("✅ Gizmobbs-specific content detected")
                elif shop_type == "logicantiq" and ("antique" in enhanced_content.lower() or "vintage" in enhanced_content.lower()):
                    print("✅ LogicAntiq-specific content detected")
                    
            else:
                all_passed = False
        
        return all_passed

    def test_clickable_images_webhook_endpoint(self):
        """Test the N8N webhook endpoint with enhanced clickable images"""
        webhook_data = {
            "store": "gizmobbs",
            "title": "Test Produit - Images Cliquables",
            "description": "Ce produit teste la nouvelle fonctionnalité d'images cliquables comme Facebook Share",
            "product_url": "https://gizmobbs.com/test-produit-cliquable",
            "image_url": "https://picsum.photos/800/600?random=webhook1"
        }
        
        success, response = self.run_test(
            "N8N Webhook - Clickable Images",
            "POST",
            "api/webhook",
            200,
            data=webhook_data
        )
        
        if success:
            status = response.get("status")
            facebook_post_id = response.get("facebook_post_id")
            instagram_post_id = response.get("instagram_post_id")
            page_name = response.get("page_name")
            message = response.get("message", "")
            clickable_image_used = response.get("clickable_image_used", False)
            
            print(f"   Status: {status}")
            print(f"   Page: {page_name}")
            print(f"   Facebook Post ID: {facebook_post_id}")
            print(f"   Instagram Post ID: {instagram_post_id}")
            print(f"   Clickable Image Used: {clickable_image_used}")
            
            # Check if clickable images feature was used
            if clickable_image_used:
                print("✅ Clickable images feature activated")
            else:
                print("⚠️  Clickable images feature not used (may be expected in test mode)")
            
            # Check Facebook posting
            if facebook_post_id:
                print("✅ Facebook post created")
                if facebook_post_id.startswith("test_"):
                    print("✅ Test mode - simulated posting")
                else:
                    print("✅ Real Facebook post created")
            else:
                print("❌ Facebook post creation failed")
                return False
            
            # Check Instagram cross-posting
            if instagram_post_id:
                print("✅ Instagram cross-posting successful")
            elif "instagram" in message.lower():
                print("⚠️  Instagram mentioned in message but no post ID")
            else:
                print("⚠️  No Instagram cross-posting (may be expected)")
            
            # Check success message mentions both platforms
            if "facebook" in message.lower() and ("instagram" in message.lower() or "cross" in message.lower()):
                print("✅ Success message mentions cross-platform posting")
            else:
                print("⚠️  Success message should mention cross-platform features")
        
        return success

    def test_webhook_with_different_shop_types(self):
        """Test webhook endpoint with different shop types for enhanced descriptions"""
        shop_types = [
            {
                "store": "outdoor",
                "title": "Sac à dos de randonnée 50L",
                "description": "Sac technique pour les longues randonnées en montagne",
                "product_url": "https://logicampoutdoor.com/sac-randonnee-50l",
                "expected_page": "outdoor"
            },
            {
                "store": "logicantiq", 
                "title": "Commode Louis XVI authentique",
                "description": "Magnifique commode d'époque en marqueterie",
                "product_url": "https://logicantiq.com/commode-louis-xvi",
                "expected_page": "antiq"
            }
        ]
        
        all_passed = True
        
        for shop_data in shop_types:
            webhook_data = {
                "store": shop_data["store"],
                "title": shop_data["title"],
                "description": shop_data["description"],
                "product_url": shop_data["product_url"],
                "image_url": f"https://picsum.photos/800/600?random={shop_data['store']}"
            }
            
            success, response = self.run_test(
                f"Webhook Enhanced - {shop_data['store'].title()}",
                "POST",
                "api/webhook",
                200,
                data=webhook_data
            )
            
            if success:
                page_name = response.get("page_name", "").lower()
                shop_type = response.get("shop_type", "")
                enhanced_content = response.get("enhanced_content", "")
                
                print(f"   Shop Type: {shop_type}")
                print(f"   Page Selected: {response.get('page_name')}")
                
                # Check if correct page was selected
                if shop_data["expected_page"] in page_name:
                    print(f"✅ Correct page selected for {shop_data['store']}")
                else:
                    print(f"⚠️  Expected page containing '{shop_data['expected_page']}', got '{page_name}'")
                
                # Check enhanced content
                if enhanced_content and len(enhanced_content) > len(shop_data["description"]):
                    print("✅ Content was enhanced")
                else:
                    print("⚠️  Content enhancement not detected")
                    
            else:
                all_passed = False
        
        return all_passed

    def test_enhanced_post_creation_endpoint(self):
        """Test the enhanced post creation with clickable images"""
        post_data = {
            "title": "Test Enhanced Post Creation",
            "description": "Testing the new enhanced post creation with clickable images functionality",
            "image_url": "https://picsum.photos/800/600?random=enhanced",
            "product_url": "https://gizmobbs.com/test-enhanced-post",
            "shop_type": "gizmobbs"
        }
        
        success, response = self.run_test(
            "Enhanced Post Creation Test",
            "POST",
            "api/test/product-post-enhanced",
            200,
            data=post_data
        )
        
        if success:
            status = response.get("status")
            test_data = response.get("test_data", {})
            features_tested = response.get("features_tested", [])
            
            print(f"   Status: {status}")
            print(f"   Features tested: {len(features_tested)}")
            
            # Check Facebook page identification
            facebook_page = test_data.get("facebook_page", {})
            if facebook_page.get("name"):
                print(f"✅ Facebook page identified: {facebook_page['name']}")
            else:
                print("❌ No Facebook page identified")
                return False
            
            # Check Instagram account detection
            instagram_account = test_data.get("instagram_account", {})
            if instagram_account.get("connected"):
                print(f"✅ Instagram account connected: @{instagram_account.get('username')}")
            else:
                print("⚠️  No Instagram account connected")
            
            # Check content preparation
            content_prepared = test_data.get("content_prepared", {})
            if content_prepared.get("facebook_content") and content_prepared.get("instagram_content"):
                print("✅ Content prepared for both platforms")
                
                # Check Instagram-specific adaptations
                instagram_content = content_prepared.get("instagram_content", "")
                if "lien en bio" in instagram_content.lower():
                    print("✅ Instagram content adapted with 'Lien en bio'")
                else:
                    print("⚠️  Instagram content missing 'Lien en bio'")
                    
            else:
                print("❌ Content preparation incomplete")
                return False
            
            # Check clickable link setup
            clickable_link = content_prepared.get("clickable_link", "")
            if clickable_link == post_data["product_url"]:
                print("✅ Clickable link correctly configured")
            else:
                print("❌ Clickable link configuration failed")
                return False
            
            # Check essential features
            essential_features = [
                "Image download and optimization",
                "Facebook page identification",
                "Clickable image data preparation"
            ]
            
            features_found = 0
            for feature in essential_features:
                if any(feature.lower() in tested.lower() for tested in features_tested):
                    features_found += 1
                    print(f"✅ Feature tested: {feature}")
                else:
                    print(f"❌ Feature not tested: {feature}")
            
            if features_found >= 2:  # At least 2 out of 3 essential features
                print("✅ Essential enhanced features working")
            else:
                print("❌ Too many essential features missing")
                return False
        
        return success

    def test_generate_enhanced_description_function(self):
        """Test the generate_enhanced_product_description function directly"""
        test_cases = [
            {
                "title": "Smartphone Ultra Premium",
                "description": "Le smartphone le plus avancé avec IA intégrée",
                "shop_type": "gizmobbs",
                "platform": "facebook"
            },
            {
                "title": "Tente 4 Saisons Professionnelle", 
                "description": "Résistante aux conditions extrêmes",
                "shop_type": "outdoor",
                "platform": "instagram"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            success, response = self.run_test(
                f"Generate Enhanced Description - {test_case['shop_type']}",
                "POST",
                "api/test/generate-description",
                200,
                data=test_case
            )
            
            if success:
                enhanced = response.get("enhanced_description", "")
                original = f"{test_case['title']}\n\n{test_case['description']}"
                
                print(f"   Original: {len(original)} chars")
                print(f"   Enhanced: {len(enhanced)} chars")
                
                # Check if content was actually enhanced
                if len(enhanced) > len(original):
                    print("✅ Description was enhanced")
                else:
                    print("⚠️  Description not significantly enhanced")
                
                # Platform-specific checks
                if test_case["platform"] == "instagram":
                    if "#" in enhanced:
                        print("✅ Hashtags added for Instagram")
                    else:
                        print("❌ Missing hashtags for Instagram")
                        all_passed = False
                        
                    if "lien en bio" in enhanced.lower():
                        print("✅ Instagram 'Lien en bio' added")
                    else:
                        print("❌ Missing Instagram 'Lien en bio'")
                        all_passed = False
                        
            else:
                all_passed = False
        
        return all_passed

    def run_all_tests(self):
        """Run all enhanced features tests"""
        print("🚀 Starting Enhanced Features Tests for Meta Publishing Platform")
        print("=" * 70)
        
        # Basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed - aborting tests")
            return False
        
        # Enhanced features tests
        tests = [
            self.test_enhanced_product_description_generation,
            self.test_generate_enhanced_description_function,
            self.test_clickable_images_webhook_endpoint,
            self.test_webhook_with_different_shop_types,
            self.test_enhanced_post_creation_endpoint
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
                self.tests_run += 1
        
        # Results
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All enhanced features tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = EnhancedFeaturesTest()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())