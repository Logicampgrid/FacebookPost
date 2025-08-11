import requests
import sys
import json
from datetime import datetime
import uuid

class FacebookPostManagerTester:
    def __init__(self, base_url="http://localhost:8001"):
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

    def test_facebook_token_debug_invalid(self):
        """Test Facebook token debug endpoint with invalid token"""
        invalid_token = "invalid_token_12345"
        success, response = self.run_test(
            "Facebook Token Debug (Invalid)",
            "GET",
            f"api/debug/facebook-token/{invalid_token}",
            200  # Endpoint should return 200 but with status: invalid
        )
        
        if success and response.get("status") == "invalid":
            print("✅ Correctly identified invalid token")
            # Check if error structure is correct for the frontend fix
            error_data = response.get("error", {})
            if isinstance(error_data, dict) and "error" in error_data:
                print("✅ Error structure supports testData.error?.error?.message access")
            else:
                print("⚠️  Error structure may not support nested error access")
            return True
        elif success:
            print(f"⚠️  Unexpected response status: {response.get('status')}")
            return False
        return success

    def test_facebook_token_debug_various_invalid_tokens(self):
        """Test Facebook token debug with various invalid token formats"""
        invalid_tokens = [
            "clearly_invalid_token",
            "EAABwzLixnjYBAGZCxyz123",  # Fake token format
            "expired_token_example",
            "",  # Empty token
            "short"  # Too short token
        ]
        
        all_passed = True
        for token in invalid_tokens:
            if not token:  # Skip empty token as it would cause URL issues
                continue
                
            success, response = self.run_test(
                f"Facebook Token Debug (Invalid: {token[:20]}...)",
                "GET",
                f"api/debug/facebook-token/{token}",
                200
            )
            
            if success:
                status = response.get("status")
                if status == "invalid":
                    print(f"✅ Token '{token[:20]}...' correctly identified as invalid")
                    # Check error message structure
                    error_data = response.get("error", {})
                    if isinstance(error_data, dict):
                        print(f"   Error structure: {list(error_data.keys())}")
                elif status == "error":
                    print(f"✅ Token '{token[:20]}...' caused error (expected for malformed tokens)")
                else:
                    print(f"⚠️  Unexpected status '{status}' for token '{token[:20]}...'")
                    all_passed = False
            else:
                all_passed = False
        
        return all_passed

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
            print(f"   App Secret: {app_secret_configured}")
            
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
            app_id = response.get("app_id")
            redirect_uri = response.get("redirect_uri")
            
            print(f"   Auth URL: {auth_url[:100]}...")
            print(f"   App ID: {app_id}")
            print(f"   Redirect URI: {redirect_uri}")
            
            if "facebook.com" in auth_url and "5664227323683118" in auth_url:
                print("✅ Valid Facebook auth URL generated")
            else:
                print("⚠️  Invalid auth URL format")
        
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

    def test_extract_links_from_text(self):
        """Test extracting links from text content"""
        test_text = "Découvrez https://www.youtube.com et https://github.com pour plus d'infos!"
        
        success, response = self.run_test(
            "Extract Links from Text",
            "POST",
            "api/text/extract-links",
            200,
            data={"text": test_text}
        )
        
        if success:
            links = response.get("links", [])
            print(f"   Found {len(links)} links")
            
            # Check if we found the expected URLs
            urls = [link.get("url") for link in links]
            expected_urls = ["https://www.youtube.com", "https://github.com"]
            
            found_youtube = any("youtube.com" in url for url in urls)
            found_github = any("github.com" in url for url in urls)
            
            if found_youtube and found_github:
                print("✅ Successfully extracted expected URLs")
                
                # Check metadata structure
                for link in links:
                    if link.get("title") and link.get("url"):
                        print(f"   Link: {link['title'][:50]}... - {link['url']}")
                    else:
                        print(f"   Link missing metadata: {link}")
                        
            else:
                print(f"⚠️  Expected URLs not found. Got: {urls}")
        
        return success

    def test_extract_links_empty_text(self):
        """Test extracting links from empty text"""
        success, response = self.run_test(
            "Extract Links (Empty Text)",
            "POST",
            "api/text/extract-links",
            200,
            data={"text": ""}
        )
        
        if success:
            links = response.get("links", [])
            if len(links) == 0:
                print("✅ Correctly returned empty links for empty text")
            else:
                print(f"⚠️  Expected no links, got {len(links)}")
        
        return success

    def test_extract_links_no_urls(self):
        """Test extracting links from text without URLs"""
        test_text = "Ceci est un texte sans aucun lien web."
        
        success, response = self.run_test(
            "Extract Links (No URLs)",
            "POST",
            "api/text/extract-links",
            200,
            data={"text": test_text}
        )
        
        if success:
            links = response.get("links", [])
            if len(links) == 0:
                print("✅ Correctly returned no links for text without URLs")
            else:
                print(f"⚠️  Expected no links, got {len(links)}")
        
        return success

    def test_link_preview_single_url(self):
        """Test getting preview for a single URL"""
        test_url = "https://www.google.com"
        
        success, response = self.run_test(
            "Link Preview (Single URL)",
            "POST",
            "api/links/preview",
            200,
            data={"url": test_url}
        )
        
        if success:
            metadata = response.get("metadata", {})
            if metadata.get("url") and metadata.get("title"):
                print(f"✅ Successfully got metadata for {test_url}")
                print(f"   Title: {metadata.get('title', 'N/A')}")
                print(f"   Description: {metadata.get('description', 'N/A')[:100]}...")
                print(f"   Site: {metadata.get('site_name', 'N/A')}")
            else:
                print(f"⚠️  Incomplete metadata: {list(metadata.keys())}")
        
        return success

    def test_link_preview_invalid_url(self):
        """Test getting preview for invalid URL"""
        test_url = "https://this-domain-definitely-does-not-exist-12345.com"
        
        success, response = self.run_test(
            "Link Preview (Invalid URL)",
            "POST",
            "api/links/preview",
            400,  # Should return 400 for invalid URLs
            data={"url": test_url}
        )
        
        return success

    def test_link_preview_malformed_url(self):
        """Test getting preview for malformed URL"""
        test_url = "not-a-valid-url"
        
        success, response = self.run_test(
            "Link Preview (Malformed URL)",
            "POST",
            "api/links/preview",
            500,  # Should return 500 for malformed URLs
            data={"url": test_url}
        )
        
        return success

def main():
    print("🚀 Starting Facebook Post Manager API Tests")
    print("=" * 50)
    
    tester = FacebookPostManagerTester()
    
    # Run all tests
    tests = [
        tester.test_health_check,
        tester.test_cors_headers,
        tester.test_facebook_config_debug,
        tester.test_facebook_auth_url_generation,
        tester.test_facebook_token_debug_invalid,
        tester.test_facebook_token_debug_various_invalid_tokens,
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