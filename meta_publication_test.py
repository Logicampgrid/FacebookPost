#!/usr/bin/env python3
"""
Comprehensive Backend API Test for Meta Publishing Platform
Tests all new publication endpoints and functionality
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class MetaPublishingAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
        icon = icons.get(level.upper(), "📝")
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{icon} [{timestamp}] {message}")
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Optional[Dict] = None, params: Optional[Dict] = None) -> tuple:
        """Run a single API test with enhanced error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        self.log(f"Testing {name}...", "TEST")
        self.log(f"  URL: {method} {url}", "INFO")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, params=params, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}", "SUCCESS")
                
                # Try to parse JSON response
                try:
                    response_data = response.json()
                    return True, response_data
                except json.JSONDecodeError:
                    return True, {"raw_response": response.text}
            else:
                error_msg = f"❌ {name} - Expected {expected_status}, got {response.status_code}"
                self.log(error_msg, "ERROR")
                
                # Try to get error details
                try:
                    error_data = response.json()
                    self.log(f"  Error details: {error_data}", "ERROR")
                    self.errors.append(f"{name}: {error_data}")
                except:
                    self.log(f"  Response text: {response.text[:200]}", "ERROR")
                    self.errors.append(f"{name}: Status {response.status_code} - {response.text[:100]}")
                
                return False, {}

        except requests.exceptions.Timeout:
            error_msg = f"❌ {name} - Request timeout (30s)"
            self.log(error_msg, "ERROR")
            self.errors.append(f"{name}: Timeout")
            return False, {}
        except requests.exceptions.ConnectionError:
            error_msg = f"❌ {name} - Connection error"
            self.log(error_msg, "ERROR")
            self.errors.append(f"{name}: Connection error")
            return False, {}
        except Exception as e:
            error_msg = f"❌ {name} - Error: {str(e)}"
            self.log(error_msg, "ERROR")
            self.errors.append(f"{name}: {str(e)}")
            return False, {}

    def test_health_endpoint(self) -> bool:
        """Test the extended health check endpoint"""
        self.log("=== TESTING HEALTH ENDPOINT ===", "INFO")
        
        success, response = self.run_test(
            "Health Check",
            "GET",
            "/api/health",
            200
        )
        
        if success and response:
            # Validate health response structure
            required_fields = ["status", "timestamp", "publication", "stores", "ngrok", "directories"]
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                self.log(f"⚠️ Health response missing fields: {missing_fields}", "WARNING")
            else:
                self.log("✅ Health response has all required fields", "SUCCESS")
                
            # Check publication info
            if "publication" in response:
                pub_info = response["publication"]
                self.log(f"  Test mode: {pub_info.get('test_mode')}", "INFO")
                self.log(f"  Stores configured: {pub_info.get('stores_configured')}/{pub_info.get('total_stores')}", "INFO")
                
            # Check stores configuration
            if "stores" in response:
                stores = response["stores"]
                self.log(f"  Found {len(stores)} stores configured", "INFO")
                for store_name, config in stores.items():
                    fb_ok = config.get("fb_page_id", False)
                    ig_ok = config.get("ig_user_id", False)
                    token_ok = config.get("access_token", False)
                    self.log(f"    {store_name}: FB={fb_ok}, IG={ig_ok}, Token={token_ok}", "INFO")
        
        return success

    def test_stores_endpoint(self) -> bool:
        """Test the stores listing endpoint"""
        self.log("=== TESTING STORES ENDPOINT ===", "INFO")
        
        success, response = self.run_test(
            "Get Stores",
            "GET",
            "/api/stores",
            200
        )
        
        if success and response:
            stores = response.get("stores", {})
            test_mode = response.get("test_mode", False)
            total_stores = response.get("total_stores", 0)
            
            self.log(f"  Test mode: {test_mode}", "INFO")
            self.log(f"  Total stores: {total_stores}", "INFO")
            
            expected_stores = ["logicantiq", "logicampoutdoor", "bergerblancsuisse", "gizmobbs"]
            for store_name in expected_stores:
                if store_name in stores:
                    store_info = stores[store_name]
                    self.log(f"  {store_name}: FB={store_info.get('facebook_configured')}, IG={store_info.get('instagram_configured')}", "INFO")
                else:
                    self.log(f"  ⚠️ Expected store '{store_name}' not found", "WARNING")
        
        return success

    def test_publications_endpoint(self) -> bool:
        """Test the publications history endpoint"""
        self.log("=== TESTING PUBLICATIONS ENDPOINT ===", "INFO")
        
        # Test without filters
        success, response = self.run_test(
            "Get Publications (no filter)",
            "GET",
            "/api/publications",
            200
        )
        
        if success and response:
            publications = response.get("publications", [])
            total = response.get("total", 0)
            self.log(f"  Found {len(publications)} publications (total: {total})", "INFO")
        
        # Test with store filter
        success2, response2 = self.run_test(
            "Get Publications (with store filter)",
            "GET",
            "/api/publications",
            200,
            params={"store": "logicantiq", "limit": 5}
        )
        
        if success2 and response2:
            publications = response2.get("publications", [])
            store_filter = response2.get("store_filter")
            self.log(f"  Filtered by store '{store_filter}': {len(publications)} publications", "INFO")
        
        return success and success2

    def test_config_endpoint(self) -> bool:
        """Test the store configuration testing endpoint"""
        self.log("=== TESTING CONFIG TEST ENDPOINT ===", "INFO")
        
        # Test valid store
        success, response = self.run_test(
            "Test Store Config (logicantiq)",
            "POST",
            "/api/test-config",
            200,
            params={"store": "logicantiq"}
        )
        
        if success and response:
            store = response.get("store")
            fb_test = response.get("facebook_test")
            ig_test = response.get("instagram_test")
            errors = response.get("errors", [])
            
            self.log(f"  Store: {store}", "INFO")
            if fb_test:
                self.log(f"  Facebook test: {fb_test.get('success', False)}", "INFO")
            if ig_test:
                self.log(f"  Instagram test: {ig_test.get('success', False)}", "INFO")
            if errors:
                self.log(f"  Errors: {errors}", "WARNING")
        
        # Test invalid store
        success2, response2 = self.run_test(
            "Test Store Config (invalid store)",
            "POST",
            "/api/test-config",
            400,
            params={"store": "invalid_store"}
        )
        
        return success and success2

    def test_publish_endpoint(self) -> bool:
        """Test the main publication endpoint with various scenarios"""
        self.log("=== TESTING PUBLISH ENDPOINT ===", "INFO")
        
        # Test 1: Valid publication request (Facebook only)
        publish_data = {
            "store": "logicantiq",
            "message": "Test publication from API test",
            "product_url": "https://example.com/product/123",
            "platforms": ["facebook"]
        }
        
        success1, response1 = self.run_test(
            "Publish to Facebook",
            "POST",
            "/api/publish",
            200,
            data=publish_data
        )
        
        if success1 and response1:
            self.log(f"  Success: {response1.get('success')}", "INFO")
            self.log(f"  Test mode: {response1.get('test_mode')}", "INFO")
            self.log(f"  Platforms: {response1.get('platforms')}", "INFO")
            if response1.get('facebook_result'):
                self.log(f"  Facebook result: {response1['facebook_result'].get('id', 'No ID')}", "INFO")
        
        # Test 2: Valid publication request (Instagram only)
        publish_data2 = {
            "store": "logicantiq",
            "message": "Test Instagram publication",
            "product_url": "https://example.com/product/456",
            "image_url": "https://via.placeholder.com/600x600.jpg",
            "platforms": ["instagram"]
        }
        
        success2, response2 = self.run_test(
            "Publish to Instagram",
            "POST",
            "/api/publish",
            200,
            data=publish_data2
        )
        
        if success2 and response2:
            if response2.get('instagram_result'):
                self.log(f"  Instagram result: {response2['instagram_result'].get('id', 'No ID')}", "INFO")
        
        # Test 3: Both platforms
        publish_data3 = {
            "store": "logicantiq",
            "message": "Test multi-platform publication",
            "product_url": "https://example.com/product/789",
            "platforms": ["facebook", "instagram"]
        }
        
        success3, response3 = self.run_test(
            "Publish to Both Platforms",
            "POST",
            "/api/publish",
            200,
            data=publish_data3
        )
        
        # Test 4: Invalid store
        invalid_data = {
            "store": "invalid_store",
            "message": "Test message",
            "product_url": "https://example.com/product",
            "platforms": ["facebook"]
        }
        
        success4, response4 = self.run_test(
            "Publish with Invalid Store",
            "POST",
            "/api/publish",
            400,
            data=invalid_data
        )
        
        # Test 5: Empty message
        empty_message_data = {
            "store": "logicantiq",
            "message": "",
            "product_url": "https://example.com/product",
            "platforms": ["facebook"]
        }
        
        success5, response5 = self.run_test(
            "Publish with Empty Message",
            "POST",
            "/api/publish",
            400,
            data=empty_message_data
        )
        
        # Test 6: Invalid platform
        invalid_platform_data = {
            "store": "logicantiq",
            "message": "Test message",
            "product_url": "https://example.com/product",
            "platforms": ["invalid_platform"]
        }
        
        success6, response6 = self.run_test(
            "Publish with Invalid Platform",
            "POST",
            "/api/publish",
            422,  # Pydantic validation error
            data=invalid_platform_data
        )
        
        return all([success1, success2, success3, success4, success5, success6])

    def test_legacy_endpoints(self) -> bool:
        """Test that existing endpoints still work"""
        self.log("=== TESTING LEGACY ENDPOINTS ===", "INFO")
        
        # Test posts endpoint
        success1, response1 = self.run_test(
            "Get Posts",
            "GET",
            "/api/posts",
            200
        )
        
        # Test webhook endpoint (GET for verification)
        success2, response2 = self.run_test(
            "Webhook Verification",
            "GET",
            "/api/webhook",
            400,  # Should fail without proper parameters
            params={"hub.mode": "subscribe", "hub.verify_token": "wrong_token", "hub.challenge": "test"}
        )
        
        return success1 and success2

    def run_all_tests(self) -> bool:
        """Run all tests and return overall success"""
        self.log("🚀 Starting Meta Publishing Platform API Tests", "INFO")
        self.log(f"📍 Testing endpoint: {self.base_url}", "INFO")
        
        start_time = datetime.now()
        
        # Run all test suites
        test_results = [
            self.test_health_endpoint(),
            self.test_stores_endpoint(),
            self.test_publications_endpoint(),
            self.test_config_endpoint(),
            self.test_publish_endpoint(),
            self.test_legacy_endpoints()
        ]
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Print summary
        self.log("=" * 50, "INFO")
        self.log("📊 TEST SUMMARY", "INFO")
        self.log(f"⏱️  Duration: {duration:.2f} seconds", "INFO")
        self.log(f"🧪 Tests run: {self.tests_run}", "INFO")
        self.log(f"✅ Tests passed: {self.tests_passed}", "SUCCESS")
        self.log(f"❌ Tests failed: {self.tests_run - self.tests_passed}", "ERROR" if self.tests_run - self.tests_passed > 0 else "INFO")
        
        if self.errors:
            self.log("🚨 ERRORS ENCOUNTERED:", "ERROR")
            for i, error in enumerate(self.errors, 1):
                self.log(f"  {i}. {error}", "ERROR")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"📈 Success rate: {success_rate:.1f}%", "SUCCESS" if success_rate >= 80 else "WARNING")
        
        overall_success = all(test_results) and len(self.errors) == 0
        
        if overall_success:
            self.log("🎉 ALL TESTS PASSED! API is working correctly.", "SUCCESS")
        else:
            self.log("⚠️ Some tests failed. Check the errors above.", "WARNING")
        
        return overall_success

def main():
    """Main test execution"""
    # Get backend URL from environment or use default
    import os
    backend_url = os.getenv("REACT_APP_BACKEND_URL", "https://auto-post-ig.preview.emergentagent.com")
    
    print(f"🔧 Backend URL: {backend_url}")
    
    # Create tester instance
    tester = MetaPublishingAPITester(backend_url)
    
    # Run all tests
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())