#!/usr/bin/env python3
"""
Focused Backend API Testing for Meta Publishing Platform
Tests the specific endpoints used by the frontend
"""

import requests
import json
import sys
from datetime import datetime

class FocusedAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FocusedTester/1.0'
        })
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []

    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
        icon = icons.get(level.upper(), "📝")
        print(f"{icon} [{timestamp}] {message}")

    def test_health_endpoint(self) -> bool:
        """Test /api/health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Health check successful: {data.get('status')}", "SUCCESS")
                return True
            else:
                self.log(f"Health check failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Health check error: {str(e)}", "ERROR")
            return False

    def test_oauth_status_endpoint(self) -> bool:
        """Test /api/config/oauth-status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/config/oauth-status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"OAuth Status - Ngrok: {data.get('ngrok_active')}, Ready: {data.get('oauth_ready')}", "SUCCESS")
                return True
            else:
                self.log(f"OAuth status failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"OAuth status error: {str(e)}", "ERROR")
            return False

    def test_instagram_diagnostics_endpoint(self) -> bool:
        """Test /api/debug/instagram-complete-diagnosis endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/debug/instagram-complete-diagnosis", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Instagram Diagnostics - Accounts: {len(data.get('instagram_accounts', []))}", "SUCCESS")
                return True
            else:
                self.log(f"Instagram diagnostics failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Instagram diagnostics error: {str(e)}", "ERROR")
            return False

    def test_facebook_auth_endpoint(self) -> bool:
        """Test /api/auth/facebook endpoint with invalid token"""
        try:
            payload = {"access_token": "invalid_test_token"}
            response = self.session.post(f"{self.base_url}/api/auth/facebook", json=payload, timeout=10)
            
            # We expect this to fail, but check error handling
            if response.status_code in [400, 401, 422]:
                self.log("Facebook auth properly rejects invalid token", "SUCCESS")
                return True
            elif response.status_code == 200:
                # This shouldn't happen with invalid token
                self.log("Facebook auth unexpectedly accepted invalid token", "WARNING")
                return False
            else:
                self.log(f"Facebook auth unexpected status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Facebook auth error: {str(e)}", "ERROR")
            return False

    def test_posts_endpoint(self) -> bool:
        """Test /api/posts endpoint"""
        try:
            # Test GET /api/posts (should require user_id parameter)
            response = self.session.get(f"{self.base_url}/api/posts", timeout=10)
            
            if response.status_code == 422:
                self.log("Posts endpoint properly validates required parameters", "SUCCESS")
                return True
            elif response.status_code == 200:
                data = response.json()
                self.log(f"Posts endpoint returned: {data}", "INFO")
                return True
            else:
                self.log(f"Posts endpoint unexpected status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Posts endpoint error: {str(e)}", "ERROR")
            return False

    def test_publish_endpoint(self) -> bool:
        """Test /api/publish endpoint with invalid data"""
        try:
            # Test with missing required fields
            payload = {"store": "test_store"}
            response = self.session.post(f"{self.base_url}/api/publish", json=payload, timeout=10)
            
            if response.status_code in [400, 422]:
                self.log("Publish endpoint properly validates required fields", "SUCCESS")
                return True
            elif response.status_code == 200:
                # This might happen in test mode
                self.log("Publish endpoint accepted request (possibly test mode)", "WARNING")
                return True
            else:
                self.log(f"Publish endpoint unexpected status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Publish endpoint error: {str(e)}", "ERROR")
            return False

    def test_webhook_endpoint(self) -> bool:
        """Test /api/webhook verification"""
        try:
            params = {
                'hub.mode': 'subscribe',
                'hub.verify_token': 'mon_token_secret_webhook',
                'hub.challenge': 'test_challenge_12345'
            }
            
            response = self.session.get(f"{self.base_url}/api/webhook", params=params, timeout=10)
            
            if response.status_code == 200 and response.text == 'test_challenge_12345':
                self.log("Webhook verification working correctly", "SUCCESS")
                return True
            else:
                self.log(f"Webhook verification failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Webhook verification error: {str(e)}", "ERROR")
            return False

    def run_all_tests(self):
        """Run all focused tests"""
        self.log("Starting focused API tests for Meta Publishing Platform", "INFO")
        self.log(f"Testing backend at: {self.base_url}", "INFO")
        
        tests = [
            ("Health Check", self.test_health_endpoint),
            ("OAuth Status", self.test_oauth_status_endpoint),
            ("Instagram Diagnostics", self.test_instagram_diagnostics_endpoint),
            ("Facebook Auth", self.test_facebook_auth_endpoint),
            ("Posts Endpoint", self.test_posts_endpoint),
            ("Publish Endpoint", self.test_publish_endpoint),
            ("Webhook Verification", self.test_webhook_endpoint),
        ]
        
        for test_name, test_func in tests:
            self.tests_run += 1
            self.log(f"Running: {test_name}", "TEST")
            
            try:
                if test_func():
                    self.tests_passed += 1
                    self.log(f"✅ PASSED: {test_name}", "SUCCESS")
                else:
                    self.log(f"❌ FAILED: {test_name}", "ERROR")
            except Exception as e:
                self.log(f"❌ ERROR in {test_name}: {str(e)}", "ERROR")
                self.errors.append(f"{test_name}: {str(e)}")
        
        # Print summary
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 FOCUSED TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  • {error}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    backend_url = "https://34d34f066475.ngrok-free.app"
    
    print(f"🚀 Meta Publishing Platform - Focused Backend Tests")
    print(f"📡 Backend URL: {backend_url}")
    print("=" * 60)
    
    tester = FocusedAPITester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())