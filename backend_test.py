import requests
import sys
import json
from datetime import datetime
import uuid

class FacebookPostManagerTester:
    def __init__(self, base_url="https://demobackend.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_id = None
        self.test_post_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, form_data=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        
        # Don't set Content-Type for form data - let requests handle it
        if not files and not form_data:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files or form_data:
                    response = requests.post(url, data=data, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2, default=str)[:200]}...")
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
        """Test Facebook auth with invalid token (should fail gracefully)"""
        success, response = self.run_test(
            "Facebook Auth (Invalid Token)",
            "POST",
            "api/auth/facebook",
            400,
            data={"access_token": "invalid_token_12345"}
        )
        return success

    def test_get_posts_without_user(self):
        """Test getting posts without user_id"""
        success, response = self.run_test(
            "Get Posts (No User)",
            "GET",
            "api/posts",
            200
        )
        if success and "posts" in response:
            print(f"   Found {len(response['posts'])} posts")
        return success

    def test_create_post_without_auth(self):
        """Test creating post without proper authentication"""
        post_data = {
            "content": "Test post content",
            "target_type": "page",
            "target_id": "test_page_id",
            "target_name": "Test Page"
        }
        
        # This should fail because we need user_id as form data
        success, response = self.run_test(
            "Create Post (No Auth)",
            "POST",
            "api/posts",
            422,  # Validation error expected
            data=post_data
        )
        return success

    def test_create_post_with_form_data(self):
        """Test creating post with form data"""
        # Create a fake user_id for testing
        test_user_id = str(uuid.uuid4())
        self.test_user_id = test_user_id
        
        # The endpoint expects form data
        form_data = {
            "content": "Test post content for Facebook",
            "target_type": "page", 
            "target_id": "test_page_123",
            "target_name": "Test Page Name",
            "user_id": test_user_id
        }
        
        success, response = self.run_test(
            "Create Post (Form Data)",
            "POST",
            "api/posts",
            200,
            data=form_data,
            form_data=True
        )
        
        if success and "post" in response:
            self.test_post_id = response["post"]["id"]
            print(f"   Created post with ID: {self.test_post_id}")
        
        return success

    def test_get_posts_with_user(self):
        """Test getting posts for specific user"""
        if not self.test_user_id:
            print("⚠️  Skipping - No test user ID available")
            return True
            
        success, response = self.run_test(
            "Get Posts (With User ID)",
            "GET",
            f"api/posts?user_id={self.test_user_id}",
            200
        )
        
        if success and "posts" in response:
            print(f"   Found {len(response['posts'])} posts for user")
        
        return success

    def test_publish_post_without_user(self):
        """Test publishing post without proper user setup"""
        if not self.test_post_id:
            print("⚠️  Skipping - No test post ID available")
            return True
            
        success, response = self.run_test(
            "Publish Post (No User Setup)",
            "POST",
            f"api/posts/{self.test_post_id}/publish",
            500  # Internal server error expected when user not found
        )
        return success

    def test_delete_post(self):
        """Test deleting a post"""
        if not self.test_post_id:
            print("⚠️  Skipping - No test post ID available")
            return True
            
        success, response = self.run_test(
            "Delete Post",
            "DELETE",
            f"api/posts/{self.test_post_id}",
            200
        )
        return success

    def test_delete_nonexistent_post(self):
        """Test deleting non-existent post"""
        fake_post_id = str(uuid.uuid4())
        success, response = self.run_test(
            "Delete Non-existent Post",
            "DELETE",
            f"api/posts/{fake_post_id}",
            404
        )
        return success

    def test_get_user_pages_nonexistent(self):
        """Test getting pages for non-existent user"""
        fake_user_id = str(uuid.uuid4())
        success, response = self.run_test(
            "Get User Pages (Non-existent)",
            "GET",
            f"api/users/{fake_user_id}/pages",
            404
        )
        return success

    def test_cors_headers(self):
        """Test CORS configuration"""
        print(f"\n🔍 Testing CORS Headers...")
        try:
            # Test with a regular GET request to see CORS headers
            response = requests.get(f"{self.base_url}/api/health")
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            print(f"   CORS Headers: {cors_headers}")
            
            # Also test OPTIONS request
            options_response = requests.options(f"{self.base_url}/api/health")
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

def main():
    print("🚀 Starting Facebook Post Manager API Tests")
    print("=" * 50)
    
    tester = FacebookPostManagerTester()
    
    # Run all tests
    tests = [
        tester.test_health_check,
        tester.test_cors_headers,
        tester.test_facebook_auth_invalid,
        tester.test_get_posts_without_user,
        tester.test_create_post_without_auth,
        tester.test_create_post_with_form_data,
        tester.test_get_posts_with_user,
        tester.test_publish_post_without_user,
        tester.test_delete_post,
        tester.test_delete_nonexistent_post,
        tester.test_get_user_pages_nonexistent
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            tester.tests_run += 1
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())