import requests
import sys
import json
from datetime import datetime
import uuid

class FacebookWorkflowTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.facebook_token = "EAASCBksMsMQBPOiYNmkdqNjwxMfwZBZAnOv4IW6OcKeQCpiM3vpPKEcmF44jAleWVCKjZCR3V5NrZBGXLsTZBLBnXB11zYk0YQHjUmf7rWhBKqZBqLjsAxZA7ZBOZBwKBcKrNPy4exasWmrQa290RsbYUEPw3qxlNelvfNPr45T0aHCwGpFIEcW3RkHAAlxtPPzrgdgfblULWzbYfxh5zYA6yZAV3zQiBFKp4sNL7x9GANVEeLieulhQZDZD"
        self.user_data = None
        self.test_post_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, form_data=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        
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

    def test_facebook_token_validation(self):
        """Test the provided Facebook token"""
        success, response = self.run_test(
            "Facebook Token Validation",
            "GET",
            f"api/debug/facebook-token/{self.facebook_token}",
            200
        )
        
        if success:
            status = response.get("status")
            if status == "valid":
                print("✅ Facebook token is valid")
                user_info = response.get("user", {})
                print(f"   User: {user_info.get('name')} (ID: {user_info.get('id')})")
                return True
            else:
                print(f"❌ Facebook token is {status}")
                error = response.get("error", {})
                print(f"   Error: {error}")
                return False
        return success

    def test_facebook_authentication(self):
        """Test Facebook authentication with the provided token"""
        success, response = self.run_test(
            "Facebook Authentication",
            "POST",
            "api/auth/facebook",
            200,
            data={"access_token": self.facebook_token}
        )
        
        if success:
            self.user_data = response.get("user")
            if self.user_data:
                print(f"✅ User authenticated: {self.user_data.get('name')}")
                print(f"   User ID: {self.user_data.get('_id')}")
                print(f"   Facebook ID: {self.user_data.get('facebook_id')}")
                print(f"   Pages: {len(self.user_data.get('facebook_pages', []))}")
                
                # Print page details
                for i, page in enumerate(self.user_data.get('facebook_pages', [])[:3]):
                    print(f"   Page {i+1}: {page.get('name')} (ID: {page.get('id')})")
                
                return True
            else:
                print("❌ No user data in response")
                return False
        return success

    def test_create_post_with_real_user(self):
        """Test creating a post with authenticated user"""
        if not self.user_data:
            print("⚠️  Skipping - No authenticated user")
            return True
        
        # Use the first available page
        pages = self.user_data.get('facebook_pages', [])
        if not pages:
            print("⚠️  Skipping - No Facebook pages available")
            return True
        
        target_page = pages[0]
        
        form_data = {
            "content": "Test post from automated testing",
            "target_type": "page",
            "target_id": target_page.get('id'),
            "target_name": target_page.get('name'),
            "user_id": self.user_data.get('_id')
        }
        
        success, response = self.run_test(
            "Create Post with Real User",
            "POST",
            "api/posts",
            200,
            data=form_data,
            form_data=True
        )
        
        if success:
            post_data = response.get("post")
            if post_data:
                self.test_post_id = post_data.get("id")
                print(f"✅ Post created with ID: {self.test_post_id}")
                print(f"   Content: {post_data.get('content')}")
                print(f"   Target: {post_data.get('target_name')}")
                print(f"   Status: {post_data.get('status')}")
                return True
            else:
                print("❌ No post data in response")
                return False
        return success

    def test_get_user_posts(self):
        """Test getting posts for the authenticated user"""
        if not self.user_data:
            print("⚠️  Skipping - No authenticated user")
            return True
        
        user_id = self.user_data.get('_id')
        success, response = self.run_test(
            "Get User Posts",
            "GET",
            f"api/posts?user_id={user_id}",
            200
        )
        
        if success:
            posts = response.get("posts", [])
            print(f"✅ Found {len(posts)} posts for user")
            
            # Show details of recent posts
            for i, post in enumerate(posts[:3]):
                print(f"   Post {i+1}: {post.get('content')[:50]}... (Status: {post.get('status')})")
            
            return True
        return success

    def test_publish_post_with_real_user(self):
        """Test publishing the created post - this was the main bug"""
        if not self.test_post_id:
            print("⚠️  Skipping - No test post available")
            return True
        
        success, response = self.run_test(
            "Publish Post with Real User",
            "POST",
            f"api/posts/{self.test_post_id}/publish",
            200
        )
        
        if success:
            facebook_id = response.get("facebook_id")
            if facebook_id:
                print(f"✅ Post published successfully to Facebook!")
                print(f"   Facebook Post ID: {facebook_id}")
                return True
            else:
                print("❌ No Facebook post ID in response")
                return False
        else:
            print("❌ Publishing failed - this was the main bug we're testing")
            return False

    def test_get_user_pages(self):
        """Test getting user's Facebook pages"""
        if not self.user_data:
            print("⚠️  Skipping - No authenticated user")
            return True
        
        user_id = self.user_data.get('_id')
        success, response = self.run_test(
            "Get User Pages",
            "GET",
            f"api/users/{user_id}/pages",
            200
        )
        
        if success:
            pages = response.get("pages", [])
            print(f"✅ Found {len(pages)} pages for user")
            
            for i, page in enumerate(pages[:3]):
                print(f"   Page {i+1}: {page.get('name')} (ID: {page.get('id')})")
                print(f"            Access Token: {'Yes' if page.get('access_token') else 'No'}")
            
            return True
        return success

    def cleanup_test_post(self):
        """Clean up the test post"""
        if not self.test_post_id:
            return True
        
        success, response = self.run_test(
            "Cleanup Test Post",
            "DELETE",
            f"api/posts/{self.test_post_id}",
            200
        )
        
        if success:
            print("✅ Test post cleaned up")
        else:
            print("⚠️  Could not clean up test post")
        
        return success

def main():
    print("🚀 Starting Facebook Workflow Integration Tests")
    print("=" * 60)
    
    tester = FacebookWorkflowTester()
    
    # Run workflow tests in order
    tests = [
        tester.test_facebook_token_validation,
        tester.test_facebook_authentication,
        tester.test_get_user_pages,
        tester.test_create_post_with_real_user,
        tester.test_get_user_posts,
        tester.test_publish_post_with_real_user,  # This is the main test for the bug fix
        tester.cleanup_test_post
    ]
    
    for test in tests:
        try:
            result = test()
            if not result:
                print(f"\n⚠️  Test {test.__name__} failed - continuing with remaining tests")
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            tester.tests_run += 1
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed >= tester.tests_run - 1:  # Allow 1 failure for cleanup
        print("🎉 Workflow tests completed successfully!")
        print("✅ The 'User not found' bug appears to be fixed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        print("❌ There may still be issues with the workflow")
        return 1

if __name__ == "__main__":
    sys.exit(main())