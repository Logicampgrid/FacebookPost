#!/usr/bin/env python3
"""
Backend API Testing for Meta Publishing Platform - 3 Stores Testing
Tests the 3 configured stores: gizmobbs, logicantiq, outdoor
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

class StoresAPITester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'StoresAPITester/1.0'
        })
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []
        self.stores = ["gizmobbs", "logicantiq", "outdoor"]

    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
        icon = icons.get(level.upper(), "📝")
        print(f"{icon} [{timestamp}] {message}")

    def run_test(self, name: str, test_func, *args, **kwargs) -> bool:
        """Run a single test with error handling"""
        self.tests_run += 1
        self.log(f"Running test: {name}", "TEST")
        
        try:
            result = test_func(*args, **kwargs)
            if result:
                self.tests_passed += 1
                self.log(f"✅ PASSED: {name}", "SUCCESS")
            else:
                self.log(f"❌ FAILED: {name}", "ERROR")
            return result
        except Exception as e:
            self.log(f"❌ ERROR in {name}: {str(e)}", "ERROR")
            self.errors.append(f"{name}: {str(e)}")
            return False

    def test_health_check(self) -> bool:
        """Test basic health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Health check failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"Health check response: {json.dumps(data, indent=2)}", "INFO")
            
            if data.get('status') != 'healthy':
                self.log(f"Service not healthy: {data.get('status')}", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"Health check error: {str(e)}", "ERROR")
            return False

    def test_store_publish_facebook(self, store: str) -> bool:
        """Test Facebook publishing for a specific store"""
        try:
            payload = {
                "store": store,
                "message": f"Test Facebook post from {store} - {datetime.now().strftime('%H:%M:%S')}",
                "product_url": "https://example.com/test-product",
                "platforms": ["facebook"]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/publish",
                json=payload,
                timeout=30
            )
            
            self.log(f"Facebook publish response for {store}: Status {response.status_code}", "INFO")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Facebook publish data for {store}: {json.dumps(data, indent=2)}", "INFO")
                
                # Check response structure
                if data.get("success") and data.get("facebook_result"):
                    self.log(f"✅ Facebook publish successful for {store}", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Facebook publish failed for {store}: {data.get('errors', 'Unknown error')}", "ERROR")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log(f"❌ Facebook publish error for {store}: {json.dumps(error_data, indent=2)}", "ERROR")
                except:
                    self.log(f"❌ Facebook publish error for {store}: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error testing Facebook publish for {store}: {str(e)}", "ERROR")
            return False

    def test_store_publish_instagram(self, store: str) -> bool:
        """Test Instagram publishing for a specific store"""
        try:
            payload = {
                "store": store,
                "message": f"Test Instagram post from {store} - {datetime.now().strftime('%H:%M:%S')}",
                "product_url": "https://example.com/test-product",
                "image_url": "https://picsum.photos/800/600?random=" + str(int(time.time())),
                "platforms": ["instagram"]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/publish",
                json=payload,
                timeout=30
            )
            
            self.log(f"Instagram publish response for {store}: Status {response.status_code}", "INFO")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Instagram publish data for {store}: {json.dumps(data, indent=2)}", "INFO")
                
                # Check response structure
                if data.get("success") and data.get("instagram_result"):
                    self.log(f"✅ Instagram publish successful for {store}", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Instagram publish failed for {store}: {data.get('errors', 'Unknown error')}", "ERROR")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log(f"❌ Instagram publish error for {store}: {json.dumps(error_data, indent=2)}", "ERROR")
                except:
                    self.log(f"❌ Instagram publish error for {store}: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error testing Instagram publish for {store}: {str(e)}", "ERROR")
            return False

    def test_store_publish_both_platforms(self, store: str) -> bool:
        """Test publishing to both Facebook and Instagram for a specific store"""
        try:
            payload = {
                "store": store,
                "message": f"Test multi-platform post from {store} - {datetime.now().strftime('%H:%M:%S')}",
                "product_url": "https://example.com/test-product",
                "image_url": "https://picsum.photos/800/600?random=" + str(int(time.time())),
                "platforms": ["facebook", "instagram"]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/publish",
                json=payload,
                timeout=45
            )
            
            self.log(f"Multi-platform publish response for {store}: Status {response.status_code}", "INFO")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Multi-platform publish data for {store}: {json.dumps(data, indent=2)}", "INFO")
                
                # Check response structure
                success = data.get("success", False)
                fb_result = data.get("facebook_result")
                ig_result = data.get("instagram_result")
                
                if success and fb_result and ig_result:
                    self.log(f"✅ Multi-platform publish successful for {store}", "SUCCESS")
                    return True
                else:
                    errors = data.get('errors', [])
                    self.log(f"❌ Multi-platform publish partial/failed for {store}: {errors}", "ERROR")
                    return False
            else:
                try:
                    error_data = response.json()
                    self.log(f"❌ Multi-platform publish error for {store}: {json.dumps(error_data, indent=2)}", "ERROR")
                except:
                    self.log(f"❌ Multi-platform publish error for {store}: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error testing multi-platform publish for {store}: {str(e)}", "ERROR")
            return False

    def test_invalid_store(self) -> bool:
        """Test error handling for invalid store"""
        try:
            payload = {
                "store": "invalid_store",
                "message": "Test message",
                "product_url": "https://example.com/test-product",
                "platforms": ["facebook"]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/publish",
                json=payload,
                timeout=10
            )
            
            # Should return error status
            if response.status_code in [400, 422]:
                try:
                    data = response.json()
                    self.log(f"✅ Invalid store properly rejected: {data.get('detail', 'No detail')}", "SUCCESS")
                    return True
                except:
                    self.log(f"✅ Invalid store properly rejected with status {response.status_code}", "SUCCESS")
                    return True
            else:
                self.log(f"❌ Invalid store not properly rejected, got status {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error testing invalid store: {str(e)}", "ERROR")
            return False

    def test_oauth_status(self) -> bool:
        """Test OAuth configuration status"""
        try:
            response = self.session.get(f"{self.base_url}/api/config/oauth-status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"OAuth status: {json.dumps(data, indent=2)}", "INFO")
                
                oauth_ready = data.get("oauth_ready", False)
                facebook_configured = data.get("facebook_app_configured", False)
                
                if facebook_configured:
                    self.log("✅ Facebook app is configured", "SUCCESS")
                else:
                    self.log("⚠️ Facebook app not configured", "WARNING")
                
                if oauth_ready:
                    self.log("✅ OAuth is ready", "SUCCESS")
                else:
                    self.log("⚠️ OAuth not ready", "WARNING")
                
                return True
            else:
                self.log(f"OAuth status check failed with status {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Error testing OAuth status: {str(e)}", "ERROR")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests for the 3 stores"""
        self.log("Starting comprehensive API tests for 3 stores (gizmobbs, logicantiq, outdoor)", "INFO")
        self.log(f"Testing backend at: {self.base_url}", "INFO")
        
        # Test basic connectivity first
        if not self.run_test("Health Check", self.test_health_check):
            self.log("❌ Basic connectivity failed - stopping tests", "ERROR")
            return self.get_summary()
        
        # Test OAuth configuration
        self.run_test("OAuth Status Check", self.test_oauth_status)
        
        # Test invalid store handling
        self.run_test("Invalid Store Handling", self.test_invalid_store)
        
        # Test each store individually
        for store in self.stores:
            self.log(f"\n🏪 Testing store: {store.upper()}", "INFO")
            
            # Test Facebook publishing
            self.run_test(f"{store} - Facebook Publishing", self.test_store_publish_facebook, store)
            
            # Wait a bit between requests to avoid rate limiting
            time.sleep(2)
            
            # Test Instagram publishing
            self.run_test(f"{store} - Instagram Publishing", self.test_store_publish_instagram, store)
            
            # Wait a bit between requests
            time.sleep(2)
            
            # Test multi-platform publishing
            self.run_test(f"{store} - Multi-platform Publishing", self.test_store_publish_both_platforms, store)
            
            # Wait between stores
            time.sleep(3)
        
        return self.get_summary()

    def get_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        return {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'tests_failed': self.tests_run - self.tests_passed,
            'success_rate': success_rate,
            'errors': self.errors,
            'status': 'PASSED' if self.tests_passed == self.tests_run else 'FAILED'
        }

def main():
    """Main test execution"""
    print(f"🚀 Meta Publishing Platform - 3 Stores Backend API Tests")
    print(f"📡 Backend URL: http://localhost:8001")
    print(f"🏪 Testing stores: gizmobbs, logicantiq, outdoor")
    print("=" * 80)
    
    # Initialize tester
    tester = StoresAPITester()
    
    # Run all tests
    summary = tester.run_all_tests()
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Run: {summary['tests_run']}")
    print(f"Tests Passed: {summary['tests_passed']}")
    print(f"Tests Failed: {summary['tests_failed']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Overall Status: {summary['status']}")
    
    if summary['errors']:
        print("\n❌ ERRORS ENCOUNTERED:")
        for error in summary['errors']:
            print(f"  • {error}")
    
    print("\n🎯 STORES FUNCTIONALITY ASSESSMENT:")
    if summary['success_rate'] >= 80:
        print("✅ All 3 stores appear to be working correctly")
        print("✅ Facebook and Instagram publishing functional")
    else:
        print("⚠️ Some stores may have issues")
        print("⚠️ Check individual store configurations")
    
    # Return appropriate exit code
    return 0 if summary['status'] == 'PASSED' else 1

if __name__ == "__main__":
    sys.exit(main())