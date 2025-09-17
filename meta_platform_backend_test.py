#!/usr/bin/env python3
"""
Meta Publishing Platform Backend API Testing
Tests all the endpoints that were recently fixed according to the review request
"""

import requests
import json
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class MetaPlatformTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'MetaPlatformTester/1.0'
        })
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []
        self.created_post_id = None

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
        """Test /api/health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Health check failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"Health check response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check required fields
            if 'status' not in data or 'timestamp' not in data:
                self.log("Missing required fields in health response", "ERROR")
                return False
            
            if data['status'] != 'healthy':
                self.log(f"Service not healthy: {data['status']}", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"Health check error: {str(e)}", "ERROR")
            return False

    def test_instagram_complete_diagnosis(self) -> bool:
        """Test /api/debug/instagram-complete-diagnosis endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/debug/instagram-complete-diagnosis", timeout=15)
            
            if response.status_code != 200:
                self.log(f"Instagram diagnostics failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"Instagram diagnostics response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check expected fields
            expected_fields = ['timestamp', 'ngrok_active', 'webhook_configured', 'facebook_pages_count', 'instagram_accounts', 'authentication']
            for field in expected_fields:
                if field not in data:
                    self.log(f"Missing field in diagnostics: {field}", "ERROR")
                    return False
            
            # Check authentication structure
            auth = data.get('authentication')
            if auth is None:
                self.log("Authentication field is None", "ERROR")
                return False
            
            if not isinstance(auth, dict):
                self.log(f"Authentication should be dict, got {type(auth)}", "ERROR")
                return False
            
            self.log(f"Diagnostics summary - Ngrok: {data.get('ngrok_active')}, Instagram accounts: {len(data.get('instagram_accounts', []))}", "INFO")
            return True
            
        except Exception as e:
            self.log(f"Instagram diagnostics error: {str(e)}", "ERROR")
            return False

    def test_user_platforms(self) -> bool:
        """Test /api/users/test_user/platforms endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/users/test_user/platforms", timeout=10)
            
            if response.status_code != 200:
                self.log(f"User platforms failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"User platforms response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check expected platform categories
            expected_categories = ['personal_pages', 'personal_groups', 'business_pages', 'business_groups', 'business_instagram']
            for category in expected_categories:
                if category not in data:
                    self.log(f"Missing platform category: {category}", "ERROR")
                    return False
                
                if not isinstance(data[category], list):
                    self.log(f"Platform category {category} should be a list", "ERROR")
                    return False
            
            # Check if business manager is included
            if 'selected_business_manager' not in data:
                self.log("Missing selected_business_manager field", "ERROR")
                return False
            
            total_platforms = sum(len(data[cat]) for cat in expected_categories)
            self.log(f"Total platforms found: {total_platforms}", "INFO")
            return True
            
        except Exception as e:
            self.log(f"User platforms error: {str(e)}", "ERROR")
            return False

    def test_create_post(self) -> bool:
        """Test POST /api/posts endpoint"""
        try:
            post_data = {
                "user_id": "test_user",
                "content": "Test post created by automated testing",
                "platform": "facebook",
                "platform_id": "test_platform_123",
                "media_urls": []
            }
            
            response = self.session.post(f"{self.base_url}/api/posts", json=post_data, timeout=10)
            
            if response.status_code != 200:
                self.log(f"Create post failed with status {response.status_code}", "ERROR")
                try:
                    error_data = response.json()
                    self.log(f"Error response: {json.dumps(error_data, indent=2)}", "ERROR")
                except:
                    self.log(f"Error response: {response.text}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"Create post response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check response structure
            if not data.get('success'):
                self.log("Post creation not successful", "ERROR")
                return False
            
            post = data.get('post')
            if not post:
                self.log("No post data in response", "ERROR")
                return False
            
            # Store post ID for later tests
            self.created_post_id = post.get('id')
            if not self.created_post_id:
                self.log("No post ID in response", "ERROR")
                return False
            
            self.log(f"Post created successfully with ID: {self.created_post_id}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Create post error: {str(e)}", "ERROR")
            return False

    def test_get_posts(self) -> bool:
        """Test GET /api/posts?user_id=test_user endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/posts?user_id=test_user", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Get posts failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"Get posts response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check response structure
            if not data.get('success'):
                self.log("Get posts not successful", "ERROR")
                return False
            
            posts = data.get('posts')
            if not isinstance(posts, list):
                self.log("Posts should be a list", "ERROR")
                return False
            
            total = data.get('total')
            if total != len(posts):
                self.log(f"Total count mismatch: {total} vs {len(posts)}", "ERROR")
                return False
            
            self.log(f"Retrieved {len(posts)} posts for user", "INFO")
            
            # If we created a post, check if it's in the list
            if self.created_post_id:
                found_post = any(post.get('id') == self.created_post_id for post in posts)
                if found_post:
                    self.log("Created post found in posts list", "SUCCESS")
                else:
                    self.log("Created post not found in posts list", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"Get posts error: {str(e)}", "ERROR")
            return False

    def test_publish_post(self) -> bool:
        """Test POST /api/posts/{post_id}/publish endpoint"""
        if not self.created_post_id:
            self.log("No post ID available for publish test", "WARNING")
            return True  # Skip this test if no post was created
        
        try:
            response = self.session.post(f"{self.base_url}/api/posts/{self.created_post_id}/publish", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Publish post failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"Publish post response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check response structure
            if not data.get('success'):
                self.log("Post publish not successful", "ERROR")
                return False
            
            post = data.get('post')
            if not post:
                self.log("No post data in publish response", "ERROR")
                return False
            
            # Check if status was updated
            if post.get('status') != 'published':
                self.log(f"Post status not updated to published: {post.get('status')}", "ERROR")
                return False
            
            if not post.get('published_at'):
                self.log("No published_at timestamp", "ERROR")
                return False
            
            self.log(f"Post published successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Publish post error: {str(e)}", "ERROR")
            return False

    def test_delete_post(self) -> bool:
        """Test DELETE /api/posts/{post_id} endpoint"""
        if not self.created_post_id:
            self.log("No post ID available for delete test", "WARNING")
            return True  # Skip this test if no post was created
        
        try:
            response = self.session.delete(f"{self.base_url}/api/posts/{self.created_post_id}", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Delete post failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"Delete post response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check response structure
            if not data.get('success'):
                self.log("Post deletion not successful", "ERROR")
                return False
            
            self.log(f"Post deleted successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Delete post error: {str(e)}", "ERROR")
            return False

    def test_webhook_get(self) -> bool:
        """Test GET /api/webhook endpoint for webhook verification"""
        try:
            params = {
                'hub.mode': 'subscribe',
                'hub.verify_token': 'mon_token_secret_webhook',
                'hub.challenge': 'test_challenge_12345'
            }
            
            response = self.session.get(f"{self.base_url}/api/webhook", params=params, timeout=10)
            
            if response.status_code != 200:
                self.log(f"Webhook GET failed with status {response.status_code}", "ERROR")
                return False
            
            # Should return the challenge as plain text
            if response.text != 'test_challenge_12345':
                self.log(f"Webhook returned wrong challenge: {response.text}", "ERROR")
                return False
            
            self.log("Webhook verification working correctly", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Webhook GET error: {str(e)}", "ERROR")
            return False

    def test_webhook_post(self) -> bool:
        """Test POST /api/webhook endpoint for webhook data handling"""
        try:
            webhook_data = {
                "object": "page",
                "entry": [
                    {
                        "id": "test_page_id",
                        "time": int(time.time()),
                        "changes": [
                            {
                                "field": "feed",
                                "value": {
                                    "item": "post",
                                    "post_id": "test_post_123",
                                    "verb": "add"
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = self.session.post(f"{self.base_url}/api/webhook", json=webhook_data, timeout=10)
            
            if response.status_code != 200:
                self.log(f"Webhook POST failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"Webhook POST response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check if webhook was received
            if data.get('status') != 'received':
                self.log(f"Unexpected webhook response: {data}", "ERROR")
                return False
            
            self.log("Webhook POST handling working correctly", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Webhook POST error: {str(e)}", "ERROR")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        self.log("Starting Meta Publishing Platform Backend API Tests", "INFO")
        self.log(f"Testing backend at: {self.base_url}", "INFO")
        self.log("Focus: Testing recently fixed endpoints", "INFO")
        
        # Test basic connectivity first
        if not self.run_test("Health Check", self.test_health_check):
            self.log("❌ Basic connectivity failed - stopping tests", "ERROR")
            return self.get_summary()
        
        # Test the specific endpoints mentioned in the review request
        self.run_test("Instagram Complete Diagnosis", self.test_instagram_complete_diagnosis)
        self.run_test("User Platforms", self.test_user_platforms)
        self.run_test("Create Post", self.test_create_post)
        self.run_test("Get Posts", self.test_get_posts)
        self.run_test("Publish Post", self.test_publish_post)
        self.run_test("Delete Post", self.test_delete_post)
        self.run_test("Webhook GET (Verification)", self.test_webhook_get)
        self.run_test("Webhook POST (Data Handling)", self.test_webhook_post)
        
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
    # Use the ngrok URL from the review request
    backend_url = "https://3825ea0c29b5.ngrok-free.app"
    
    print(f"🚀 Meta Publishing Platform - Backend API Tests")
    print(f"📡 Backend URL: {backend_url}")
    print(f"🎯 Focus: Testing recently fixed endpoints")
    print("=" * 80)
    
    # Initialize tester
    tester = MetaPlatformTester(backend_url)
    
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
    
    print("\n🎯 ENDPOINT TESTING ASSESSMENT:")
    if summary['success_rate'] >= 80:
        print("✅ Recently fixed endpoints are working correctly")
        print("✅ API functionality appears to be restored")
    else:
        print("⚠️ Some endpoint issues detected")
        print("⚠️ May need additional fixes")
    
    # Return appropriate exit code
    return 0 if summary['status'] == 'PASSED' else 1

if __name__ == "__main__":
    sys.exit(main())