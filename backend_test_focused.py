#!/usr/bin/env python3
"""
Focused Backend Test for Meta Publishing Platform
Tests the key functionality requested in the review.
"""

import requests
import sys
import json
from datetime import datetime

class MetaPublishingPlatformTester:
    def __init__(self, base_url="https://auto-fb-publisher-1.preview.emergentagent.com"):
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

    def test_health_endpoint(self):
        """Test the main health endpoint"""
        success, response = self.run_test(
            "Backend Health Check",
            "GET",
            "api/health",
            200
        )
        
        if success:
            # Verify expected response structure
            expected_fields = ["status", "backend", "mongodb", "timestamp"]
            for field in expected_fields:
                if field in response:
                    print(f"   ✅ {field}: {response[field]}")
                else:
                    print(f"   ❌ Missing field: {field}")
                    return False
            
            # Check specific values
            if response.get("status") == "healthy":
                print("   ✅ Backend status: healthy")
            else:
                print(f"   ❌ Unexpected status: {response.get('status')}")
                return False
                
            if response.get("backend") == "running":
                print("   ✅ Backend: running")
            else:
                print(f"   ❌ Backend not running: {response.get('backend')}")
                return False
                
            if response.get("mongodb") == "connected":
                print("   ✅ MongoDB: connected")
            else:
                print(f"   ❌ MongoDB not connected: {response.get('mongodb')}")
                return False
                
            # Check database counts
            database = response.get("database", {})
            if isinstance(database, dict):
                users_count = database.get("users_count", 0)
                posts_count = database.get("posts_count", 0)
                print(f"   ✅ Database - Users: {users_count}, Posts: {posts_count}")
            else:
                print("   ❌ Database info not available")
                return False
        
        return success

    def test_cors_configuration(self):
        """Test CORS configuration"""
        print(f"\n🔍 Testing CORS Configuration...")
        try:
            # Test with a regular GET request to see CORS headers
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            print(f"   CORS Headers: {cors_headers}")
            
            # Test OPTIONS request
            options_response = requests.options(f"{self.base_url}/api/health", timeout=10)
            print(f"   OPTIONS Status: {options_response.status_code}")
            
            if cors_headers['Access-Control-Allow-Origin'] or options_response.status_code == 200:
                print("✅ CORS is configured")
                self.tests_passed += 1
            else:
                print("❌ CORS headers not found")
            
            self.tests_run += 1
            return True
        except Exception as e:
            print(f"❌ CORS test failed: {e}")
            self.tests_run += 1
            return False

    def test_facebook_auth_invalid_token(self):
        """Test Facebook auth with invalid token (should fail gracefully)"""
        success, response = self.run_test(
            "Facebook Auth (Invalid Token)",
            "POST",
            "api/auth/facebook",
            400,
            data={"access_token": "invalid_token_12345"}
        )
        
        if success:
            print("   ✅ Invalid token properly rejected")
        
        return success

    def test_posts_endpoint(self):
        """Test posts endpoint"""
        success, response = self.run_test(
            "Get Posts",
            "GET",
            "api/posts",
            200
        )
        
        if success and "posts" in response:
            posts_count = len(response['posts'])
            print(f"   ✅ Found {posts_count} posts")
        
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
            graph_url = response.get("graph_url")
            app_secret_configured = response.get("app_secret_configured")
            
            print(f"   App ID: {app_id}")
            print(f"   Graph URL: {graph_url}")
            print(f"   App Secret: {'Configured' if app_secret_configured else 'Not configured'}")
            
            if app_id == "5664227323683118":
                print("   ✅ Correct Facebook App ID configured")
            else:
                print("   ⚠️  Unexpected App ID")
        
        return success

    def run_all_tests(self):
        """Run all focused tests"""
        print("=" * 60)
        print("🚀 Meta Publishing Platform - Backend Tests")
        print("=" * 60)
        
        # Core functionality tests
        self.test_health_endpoint()
        self.test_cors_configuration()
        self.test_facebook_auth_invalid_token()
        self.test_posts_endpoint()
        self.test_facebook_config_debug()
        
        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("✅ All backend tests passed!")
            return 0
        else:
            print(f"❌ {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = MetaPublishingPlatformTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())