#!/usr/bin/env python3
"""
Frontend Integration Test
Tests the Facebook Post Manager frontend integration with backend APIs
"""

import requests
import json
import time
from datetime import datetime

class FrontendIntegrationTester:
    def __init__(self, frontend_url="http://localhost:3000", backend_url="http://localhost:8001"):
        self.frontend_url = frontend_url
        self.backend_url = backend_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, test_func):
        """Run a single test"""
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            success = test_func()
            if success:
                self.tests_passed += 1
                print(f"✅ Passed")
            else:
                print(f"❌ Failed")
            return success
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_frontend_accessibility(self):
        """Test if frontend is accessible"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                if "Facebook Post Manager" in content and "root" in content:
                    print("   Frontend HTML contains expected elements")
                    return True
                else:
                    print("   Frontend HTML missing expected content")
                    return False
            else:
                print(f"   Frontend returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"   Frontend connection error: {e}")
            return False

    def test_frontend_static_assets(self):
        """Test if frontend static assets are accessible"""
        try:
            # Test JavaScript bundle
            js_response = requests.get(f"{self.frontend_url}/static/js/bundle.js", timeout=10)
            if js_response.status_code != 200:
                print(f"   JavaScript bundle not accessible: {js_response.status_code}")
                return False
            
            print(f"   JavaScript bundle size: {len(js_response.content)} bytes")
            
            # Check if bundle contains React and our components
            js_content = js_response.text
            if "React" in js_content and "FacebookLogin" in js_content:
                print("   JavaScript bundle contains expected components")
                return True
            else:
                print("   JavaScript bundle missing expected components")
                return False
                
        except Exception as e:
            print(f"   Static assets error: {e}")
            return False

    def test_backend_api_from_frontend_perspective(self):
        """Test backend APIs that frontend would call"""
        try:
            # Test health endpoint
            health_response = requests.get(f"{self.backend_url}/api/health", timeout=5)
            if health_response.status_code != 200:
                print(f"   Backend health check failed: {health_response.status_code}")
                return False
            
            # Test Facebook config endpoint
            config_response = requests.get(f"{self.backend_url}/api/debug/facebook-config", timeout=5)
            if config_response.status_code != 200:
                print(f"   Facebook config endpoint failed: {config_response.status_code}")
                return False
            
            config_data = config_response.json()
            if config_data.get("app_id") == "5664227323683118":
                print("   Backend APIs accessible with correct Facebook config")
                return True
            else:
                print("   Backend Facebook config incorrect")
                return False
                
        except Exception as e:
            print(f"   Backend API error: {e}")
            return False

    def test_facebook_token_debug_endpoint(self):
        """Test the new Facebook token debug endpoint"""
        try:
            # Test with invalid token
            invalid_token = "invalid_test_token_12345"
            response = requests.get(f"{self.backend_url}/api/debug/facebook-token/{invalid_token}", timeout=10)
            
            if response.status_code != 200:
                print(f"   Token debug endpoint returned {response.status_code}")
                return False
            
            data = response.json()
            if data.get("status") == "invalid" and "error" in data:
                print("   Token debug endpoint correctly identifies invalid tokens")
                print(f"   Error message: {data.get('error', {}).get('error', {}).get('message', 'N/A')}")
                return True
            else:
                print(f"   Unexpected response from token debug: {data}")
                return False
                
        except Exception as e:
            print(f"   Token debug endpoint error: {e}")
            return False

    def test_cors_configuration(self):
        """Test CORS configuration for frontend-backend communication"""
        try:
            # Test preflight request
            headers = {
                'Origin': self.frontend_url,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f"{self.backend_url}/api/health", headers=headers, timeout=5)
            
            # Check CORS headers in response
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            cors_methods = response.headers.get('Access-Control-Allow-Methods')
            
            if cors_origin == '*' or cors_origin == self.frontend_url:
                print(f"   CORS origin configured: {cors_origin}")
                print(f"   CORS methods: {cors_methods}")
                return True
            else:
                print(f"   CORS not properly configured. Origin: {cors_origin}")
                return False
                
        except Exception as e:
            print(f"   CORS test error: {e}")
            return False

    def test_facebook_auth_url_generation(self):
        """Test Facebook auth URL generation endpoint"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/facebook/auth-url",
                params={"redirect_uri": self.frontend_url},
                timeout=5
            )
            
            if response.status_code != 200:
                print(f"   Auth URL generation failed: {response.status_code}")
                return False
            
            data = response.json()
            auth_url = data.get("auth_url", "")
            
            if "facebook.com" in auth_url and "5664227323683118" in auth_url:
                print("   Facebook auth URL generated correctly")
                print(f"   URL contains: {auth_url[:100]}...")
                return True
            else:
                print(f"   Invalid auth URL: {auth_url}")
                return False
                
        except Exception as e:
            print(f"   Auth URL generation error: {e}")
            return False

def main():
    print("🚀 Starting Frontend Integration Tests")
    print("=" * 60)
    
    tester = FrontendIntegrationTester()
    
    # Run all tests
    tests = [
        ("Frontend Accessibility", tester.test_frontend_accessibility),
        ("Frontend Static Assets", tester.test_frontend_static_assets),
        ("Backend API Integration", tester.test_backend_api_from_frontend_perspective),
        ("Facebook Token Debug Endpoint", tester.test_facebook_token_debug_endpoint),
        ("CORS Configuration", tester.test_cors_configuration),
        ("Facebook Auth URL Generation", tester.test_facebook_auth_url_generation),
    ]
    
    for test_name, test_func in tests:
        tester.run_test(test_name, test_func)
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All integration tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    exit(main())