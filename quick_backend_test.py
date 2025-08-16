import requests
import sys
import json
from datetime import datetime

class QuickAPITester:
    def __init__(self, base_url="https://persistent-flow-1.preview.emergentagent.com"):
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
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2, default=str)[:300]}...")
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
        """Test health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        return success

    def test_facebook_auth_invalid(self):
        """Test Facebook auth with invalid token"""
        success, response = self.run_test(
            "Facebook Auth (Invalid Token)",
            "POST",
            "api/auth/facebook",
            400,
            data={"access_token": "invalid_token_12345"}
        )
        return success

    def test_get_posts(self):
        """Test getting posts"""
        success, response = self.run_test(
            "Get Posts",
            "GET",
            "api/posts",
            200
        )
        return success

    def test_facebook_config_debug(self):
        """Test Facebook configuration debug endpoint"""
        success, response = self.run_test(
            "Facebook Config Debug",
            "GET",
            "api/debug/facebook-config",
            200
        )
        
        if success:
            app_id = response.get("app_id")
            print(f"   App ID: {app_id}")
            
            if app_id == "5664227323683118":
                print("✅ Correct Facebook App ID configured")
            else:
                print("⚠️  Unexpected App ID")
        
        return success

    def test_facebook_auth_url_generation(self):
        """Test Facebook auth URL generation"""
        success, response = self.run_test(
            "Facebook Auth URL Generation",
            "GET",
            "api/facebook/auth-url?redirect_uri=http://localhost:3000",
            200
        )
        
        if success:
            auth_url = response.get("auth_url")
            scope = response.get("scope")
            
            print(f"   Auth URL: {auth_url[:100]}...")
            print(f"   Scope: {scope}")
            
            # Check for Business Manager permissions
            required_permissions = ["business_management", "read_insights"]
            permissions_found = []
            
            for perm in required_permissions:
                if perm in scope:
                    permissions_found.append(perm)
                    print(f"✅ Found required permission: {perm}")
                else:
                    print(f"❌ Missing required permission: {perm}")
            
            if "facebook.com" in auth_url and "5664227323683118" in auth_url:
                print("✅ Valid Facebook auth URL generated")
            else:
                print("⚠️  Invalid auth URL format")
        
        return success

    def test_webhook_history_endpoint(self):
        """Test the webhook history endpoint"""
        success, response = self.run_test(
            "Get Webhook History",
            "GET",
            "api/webhook-history",
            200
        )
        
        if success:
            data = response.get("data", {})
            webhook_posts = data.get("webhook_posts", [])
            shop_types_available = data.get("shop_types_available", [])
            
            print(f"   Found {len(webhook_posts)} webhook posts")
            print(f"   Available shop types: {shop_types_available}")
            
            # Check if shop types are configured correctly
            expected_shop_types = ["outdoor", "gizmobbs", "logicantiq"]
            for shop_type in expected_shop_types:
                if shop_type in shop_types_available:
                    print(f"✅ Shop type '{shop_type}' available")
                else:
                    print(f"❌ Shop type '{shop_type}' missing")
        
        return success

def main():
    print("🚀 Starting Quick Backend API Tests...")
    print("=" * 60)
    
    tester = QuickAPITester()
    
    # Run essential tests
    tests = [
        tester.test_health_check,
        tester.test_facebook_config_debug,
        tester.test_facebook_auth_url_generation,
        tester.test_facebook_auth_invalid,
        tester.test_get_posts,
        tester.test_webhook_history_endpoint,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Tests completed: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())