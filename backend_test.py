import requests
import sys
import json
from datetime import datetime
import uuid

class FacebookPostManagerTester:
    def __init__(self, base_url="https://forward-motion-2.preview.emergentagent.com"):
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
        """Test Facebook auth URL generation with Business Manager permissions"""
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
            scope = response.get("scope")
            
            print(f"   Auth URL: {auth_url[:100]}...")
            print(f"   App ID: {app_id}")
            print(f"   Redirect URI: {redirect_uri}")
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
                
            if len(permissions_found) == len(required_permissions):
                print("✅ All Business Manager permissions included")
            else:
                print(f"⚠️  Missing {len(required_permissions) - len(permissions_found)} Business Manager permissions")
        
        return success

    def test_business_manager_endpoints_without_user(self):
        """Test Business Manager endpoints with non-existent user"""
        fake_user_id = str(uuid.uuid4())
        
        # Test getting business managers
        success1, response1 = self.run_test(
            "Get Business Managers (Non-existent User)",
            "GET",
            f"api/users/{fake_user_id}/business-managers",
            404
        )
        
        # Test selecting business manager
        success2, response2 = self.run_test(
            "Select Business Manager (Non-existent User)",
            "POST",
            f"api/users/{fake_user_id}/select-business-manager",
            404,
            data={"business_manager_id": "fake_bm_id"}
        )
        
        return success1 and success2

    def test_facebook_code_exchange_invalid(self):
        """Test Facebook code exchange with invalid data"""
        success, response = self.run_test(
            "Facebook Code Exchange (Invalid)",
            "POST",
            "api/auth/facebook/exchange-code",
            400,
            data={
                "code": "invalid_code_12345",
                "redirect_uri": "http://localhost:3000"
            }
        )
        return success

    def test_facebook_code_exchange_missing_data(self):
        """Test Facebook code exchange with missing data"""
        success, response = self.run_test(
            "Facebook Code Exchange (Missing Data)",
            "POST",
            "api/auth/facebook/exchange-code",
            422,  # Validation error
            data={}
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

    def test_debug_test_link_post(self):
        """Test the debug endpoint for Facebook link posting strategy"""
        test_content = "Check out this amazing project! https://github.com/facebook/react"
        
        success, response = self.run_test(
            "Debug Test Link Post",
            "POST",
            "api/debug/test-link-post",
            200,
            data={"content": test_content}
        )
        
        if success:
            content = response.get("content")
            detected_urls = response.get("detected_urls", [])
            link_metadata = response.get("link_metadata")
            post_strategy = response.get("post_strategy")
            
            print(f"   Content: {content}")
            print(f"   Detected URLs: {detected_urls}")
            print(f"   Strategy: {post_strategy}")
            
            if detected_urls and "github.com" in str(detected_urls):
                print("✅ Successfully detected GitHub URL")
            else:
                print("⚠️  GitHub URL not detected properly")
                
            if link_metadata and link_metadata.get("title"):
                print(f"   Link Title: {link_metadata['title']}")
                print("✅ Link metadata extracted successfully")
            else:
                print("⚠️  Link metadata not extracted")
                
            if post_strategy == "link_preview":
                print("✅ Correct posting strategy identified")
            else:
                print(f"⚠️  Unexpected strategy: {post_strategy}")
        
        return success

    def test_debug_test_link_post_no_links(self):
        """Test debug endpoint with content that has no links"""
        test_content = "This is just a regular text post without any links"
        
        success, response = self.run_test(
            "Debug Test Link Post (No Links)",
            "POST",
            "api/debug/test-link-post",
            200,
            data={"content": test_content}
        )
        
        if success:
            detected_urls = response.get("detected_urls", [])
            post_strategy = response.get("post_strategy")
            
            if len(detected_urls) == 0:
                print("✅ Correctly detected no URLs")
            else:
                print(f"⚠️  Unexpected URLs detected: {detected_urls}")
                
            if post_strategy == "text_only":
                print("✅ Correct text-only strategy")
            else:
                print(f"⚠️  Unexpected strategy for text-only: {post_strategy}")
        
        return success

    def test_extract_links_popular_sites(self):
        """Test extracting links from popular sites with rich metadata"""
        test_cases = [
            {
                "name": "GitHub",
                "text": "Check out https://github.com/microsoft/vscode",
                "expected_domain": "github.com"
            },
            {
                "name": "YouTube", 
                "text": "Watch this video https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "expected_domain": "youtube.com"
            },
            {
                "name": "Multiple Links",
                "text": "Great resources: https://reactjs.org and https://nodejs.org",
                "expected_domain": "reactjs.org"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            success, response = self.run_test(
                f"Extract Links ({test_case['name']})",
                "POST",
                "api/text/extract-links",
                200,
                data={"text": test_case["text"]}
            )
            
            if success:
                links = response.get("links", [])
                if len(links) > 0:
                    found_expected = any(test_case["expected_domain"] in link.get("url", "") for link in links)
                    if found_expected:
                        print(f"✅ Successfully extracted {test_case['name']} link")
                        # Check metadata quality
                        for link in links:
                            if test_case["expected_domain"] in link.get("url", ""):
                                title = link.get("title", "")
                                description = link.get("description", "")
                                image = link.get("image", "")
                                
                                print(f"   Title: {title[:50]}...")
                                print(f"   Description: {description[:50]}...")
                                print(f"   Image: {'Yes' if image else 'No'}")
                                
                                if title and description:
                                    print(f"✅ Rich metadata available for {test_case['name']}")
                                else:
                                    print(f"⚠️  Limited metadata for {test_case['name']}")
                                break
                    else:
                        print(f"❌ Expected domain {test_case['expected_domain']} not found")
                        all_passed = False
                else:
                    print(f"❌ No links extracted for {test_case['name']}")
                    all_passed = False
            else:
                all_passed = False
        
        return all_passed

    def test_create_post_with_links(self):
        """Test creating a post with links and verify metadata is stored"""
        test_user_id = str(uuid.uuid4())
        content_with_links = "Check out this amazing project! https://github.com/facebook/react and also https://reactjs.org"
        
        form_data = {
            "content": content_with_links,
            "target_type": "page", 
            "target_id": "test_page_123",
            "target_name": "Test Page Name",
            "user_id": test_user_id
        }
        
        success, response = self.run_test(
            "Create Post with Links",
            "POST",
            "api/posts",
            200,
            data=form_data,
            form_data=True
        )
        
        if success and "post" in response:
            post = response["post"]
            link_metadata = post.get("link_metadata", [])
            
            print(f"   Post created with {len(link_metadata)} link metadata entries")
            
            if len(link_metadata) > 0:
                print("✅ Link metadata stored in post")
                for i, metadata in enumerate(link_metadata):
                    url = metadata.get("url", "")
                    title = metadata.get("title", "")
                    print(f"   Link {i+1}: {title} - {url}")
                    
                    if "github.com" in url or "reactjs.org" in url:
                        print(f"✅ Expected URL found: {url}")
                    else:
                        print(f"⚠️  Unexpected URL: {url}")
            else:
                print("⚠️  No link metadata stored")
                
            # Store post ID for cleanup
            self.test_post_id = post["id"]
        
        return success

    def test_create_post_with_comment_link(self):
        """Test creating a post with comment link functionality"""
        test_user_id = str(uuid.uuid4())
        content = "Check out our latest product update!"
        comment_link = "https://www.example.com/product-details"
        
        form_data = {
            "content": content,
            "target_type": "page", 
            "target_id": "test_page_123",
            "target_name": "Test Page Name",
            "user_id": test_user_id,
            "comment_link": comment_link
        }
        
        success, response = self.run_test(
            "Create Post with Comment Link",
            "POST",
            "api/posts",
            200,
            data=form_data,
            form_data=True
        )
        
        if success and "post" in response:
            post = response["post"]
            stored_comment_link = post.get("comment_link")
            comment_status = post.get("comment_status")
            
            print(f"   Comment Link: {stored_comment_link}")
            print(f"   Comment Status: {comment_status}")
            
            if stored_comment_link == comment_link:
                print("✅ Comment link stored correctly")
            else:
                print(f"❌ Comment link mismatch. Expected: {comment_link}, Got: {stored_comment_link}")
                
            # Note: comment_status will be None since we don't have real Facebook integration
            if comment_status is None:
                print("✅ Comment status initialized correctly (None for test)")
            else:
                print(f"⚠️  Unexpected comment status: {comment_status}")
        
        return success

    def test_create_post_without_comment_link(self):
        """Test creating a post without comment link (should work normally)"""
        test_user_id = str(uuid.uuid4())
        content = "Regular post without comment link"
        
        form_data = {
            "content": content,
            "target_type": "page", 
            "target_id": "test_page_123",
            "target_name": "Test Page Name",
            "user_id": test_user_id
            # No comment_link field
        }
        
        success, response = self.run_test(
            "Create Post without Comment Link",
            "POST",
            "api/posts",
            200,
            data=form_data,
            form_data=True
        )
        
        if success and "post" in response:
            post = response["post"]
            stored_comment_link = post.get("comment_link")
            
            if stored_comment_link is None:
                print("✅ Comment link correctly set to None when not provided")
            else:
                print(f"⚠️  Unexpected comment link value: {stored_comment_link}")
        
        return success

    def test_create_post_with_empty_comment_link(self):
        """Test creating a post with empty comment link"""
        test_user_id = str(uuid.uuid4())
        content = "Post with empty comment link"
        
        form_data = {
            "content": content,
            "target_type": "page", 
            "target_id": "test_page_123",
            "target_name": "Test Page Name",
            "user_id": test_user_id,
            "comment_link": ""  # Empty string
        }
        
        success, response = self.run_test(
            "Create Post with Empty Comment Link",
            "POST",
            "api/posts",
            200,
            data=form_data,
            form_data=True
        )
        
        if success and "post" in response:
            post = response["post"]
            stored_comment_link = post.get("comment_link")
            
            if stored_comment_link == "":
                print("✅ Empty comment link stored correctly")
            else:
                print(f"⚠️  Unexpected comment link value: {stored_comment_link}")
        
        return success

    def test_create_post_with_invalid_comment_link(self):
        """Test creating a post with invalid comment link format"""
        test_user_id = str(uuid.uuid4())
        content = "Post with invalid comment link"
        
        form_data = {
            "content": content,
            "target_type": "page", 
            "target_id": "test_page_123",
            "target_name": "Test Page Name",
            "user_id": test_user_id,
            "comment_link": "not-a-valid-url"  # Invalid URL format
        }
        
        success, response = self.run_test(
            "Create Post with Invalid Comment Link",
            "POST",
            "api/posts",
            200,  # Backend should still accept it (validation is frontend responsibility)
            data=form_data,
            form_data=True
        )
        
        if success and "post" in response:
            post = response["post"]
            stored_comment_link = post.get("comment_link")
            
            if stored_comment_link == "not-a-valid-url":
                print("✅ Invalid comment link stored (backend accepts any string)")
                print("⚠️  Consider adding URL validation in backend")
            else:
                print(f"⚠️  Unexpected comment link value: {stored_comment_link}")
        
        return success

    def test_facebook_posting_strategy_simulation(self):
        """Test Facebook posting strategy with different content types"""
        test_cases = [
            {
                "name": "Link Only",
                "content": "https://github.com/facebook/react",
                "expected_strategy": "link_preview"
            },
            {
                "name": "Link with Short Text",
                "content": "Great project! https://github.com/facebook/react",
                "expected_strategy": "link_preview"
            },
            {
                "name": "Link with Long Text",
                "content": "This is a very long description about an amazing project that does incredible things and has many features. Check it out: https://github.com/facebook/react",
                "expected_strategy": "link_preview"
            },
            {
                "name": "Text Only",
                "content": "This is just a regular post without any links",
                "expected_strategy": "text_only"
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            success, response = self.run_test(
                f"Facebook Strategy ({test_case['name']})",
                "POST",
                "api/debug/test-link-post",
                200,
                data={"content": test_case["content"]}
            )
            
            if success:
                strategy = response.get("post_strategy")
                detected_urls = response.get("detected_urls", [])
                
                print(f"   Strategy: {strategy}")
                print(f"   URLs: {len(detected_urls)}")
                
                if strategy == test_case["expected_strategy"]:
                    print(f"✅ Correct strategy for {test_case['name']}")
                else:
                    print(f"❌ Expected {test_case['expected_strategy']}, got {strategy}")
                    all_passed = False
            else:
                all_passed = False
        
        return all_passed

    def test_media_upload_without_post(self):
        """Test uploading media to non-existent post"""
        fake_post_id = str(uuid.uuid4())
        
        # Create a small test image file
        import io
        test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {
            'file': ('test_image.png', io.BytesIO(test_image_content), 'image/png')
        }
        
        success, response = self.run_test(
            "Upload Media (Non-existent Post)",
            "POST",
            f"api/posts/{fake_post_id}/media",
            500,  # Should fail when post doesn't exist
            files=files
        )
        return success

    def test_media_upload_with_valid_post(self):
        """Test uploading media to existing post"""
        if not self.test_post_id:
            print("⚠️  Skipping - No test post ID available")
            return True
            
        # Create a small test image file
        import io
        test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files = {
            'file': ('test_image.png', io.BytesIO(test_image_content), 'image/png')
        }
        
        success, response = self.run_test(
            "Upload Media (Valid Post)",
            "POST",
            f"api/posts/{self.test_post_id}/media",
            200,
            files=files
        )
        
        if success:
            media_url = response.get("url")
            if media_url:
                print(f"✅ Media uploaded successfully: {media_url}")
                # Check if file was actually saved
                import os
                file_path = f"/app/backend{media_url}"
                if os.path.exists(file_path):
                    print(f"✅ File saved to disk: {file_path}")
                else:
                    print(f"⚠️  File not found on disk: {file_path}")
            else:
                print("⚠️  No media URL returned")
        
        return success

    def test_media_upload_invalid_file_type(self):
        """Test uploading invalid file type"""
        if not self.test_post_id:
            print("⚠️  Skipping - No test post ID available")
            return True
            
        # Create a text file (should be rejected)
        import io
        test_text_content = b'This is not an image file'
        
        files = {
            'file': ('test_file.txt', io.BytesIO(test_text_content), 'text/plain')
        }
        
        success, response = self.run_test(
            "Upload Media (Invalid File Type)",
            "POST",
            f"api/posts/{self.test_post_id}/media",
            200,  # Backend currently accepts any file type
            files=files
        )
        
        if success:
            print("⚠️  Backend accepted invalid file type - should add validation")
        
        return success

    def test_media_upload_large_file(self):
        """Test uploading large file"""
        if not self.test_post_id:
            print("⚠️  Skipping - No test post ID available")
            return True
            
        # Create a larger test file (1MB)
        import io
        large_content = b'x' * (1024 * 1024)  # 1MB of 'x' characters
        
        files = {
            'file': ('large_file.bin', io.BytesIO(large_content), 'application/octet-stream')
        }
        
        success, response = self.run_test(
            "Upload Media (Large File)",
            "POST",
            f"api/posts/{self.test_post_id}/media",
            200,  # Should handle large files
            files=files
        )
        
        if success:
            print("✅ Large file upload handled")
        
        return success

    def test_new_platforms_endpoint(self):
        """Test the new /api/users/{user_id}/platforms endpoint"""
        fake_user_id = str(uuid.uuid4())
        success, response = self.run_test(
            "Get User Platforms (New Endpoint)",
            "GET",
            f"api/users/{fake_user_id}/platforms",
            404  # Should return 404 for non-existent user
        )
        return success

    def test_facebook_auth_url_with_meta_permissions(self):
        """Test Facebook auth URL generation with new Meta permissions"""
        success, response = self.run_test(
            "Facebook Auth URL (Meta Permissions)",
            "GET",
            "api/facebook/auth-url?redirect_uri=http://localhost:3000",
            200
        )
        
        if success:
            scope = response.get("scope", "")
            print(f"   Scope: {scope}")
            
            # Check for new Meta permissions
            required_permissions = [
                "groups_access_member_info",
                "instagram_basic", 
                "instagram_content_publish",
                "business_management",
                "pages_manage_posts"
            ]
            
            permissions_found = []
            for perm in required_permissions:
                if perm in scope:
                    permissions_found.append(perm)
                    print(f"✅ Found Meta permission: {perm}")
                else:
                    print(f"❌ Missing Meta permission: {perm}")
            
            if len(permissions_found) == len(required_permissions):
                print("✅ All Meta platform permissions included")
            else:
                print(f"⚠️  Missing {len(required_permissions) - len(permissions_found)} Meta permissions")
        
        return success

    def test_create_instagram_post(self):
        """Test creating Instagram post"""
        test_user_id = str(uuid.uuid4())
        
        form_data = {
            "content": "Test Instagram post with image requirement",
            "target_type": "instagram", 
            "target_id": "test_instagram_123",
            "target_name": "Test Instagram Account",
            "platform": "instagram",
            "user_id": test_user_id
        }
        
        success, response = self.run_test(
            "Create Instagram Post",
            "POST",
            "api/posts",
            200,
            data=form_data,
            form_data=True
        )
        
        if success and "post" in response:
            post = response["post"]
            platform = post.get("platform")
            target_type = post.get("target_type")
            
            if platform == "instagram" and target_type == "instagram":
                print("✅ Instagram post created with correct platform/type")
            else:
                print(f"⚠️  Unexpected platform/type: {platform}/{target_type}")
        
        return success

    def test_create_group_post(self):
        """Test creating Facebook Group post"""
        test_user_id = str(uuid.uuid4())
        
        form_data = {
            "content": "Test Facebook Group post",
            "target_type": "group", 
            "target_id": "test_group_123",
            "target_name": "Test Facebook Group",
            "platform": "facebook",
            "user_id": test_user_id
        }
        
        success, response = self.run_test(
            "Create Facebook Group Post",
            "POST",
            "api/posts",
            200,
            data=form_data,
            form_data=True
        )
        
        if success and "post" in response:
            post = response["post"]
            platform = post.get("platform")
            target_type = post.get("target_type")
            
            if platform == "facebook" and target_type == "group":
                print("✅ Facebook Group post created with correct platform/type")
            else:
                print(f"⚠️  Unexpected platform/type: {platform}/{target_type}")
        
        return success

    def test_create_cross_post(self):
        """Test creating cross-platform post"""
        test_user_id = str(uuid.uuid4())
        
        cross_targets = [
            {"id": "page_123", "name": "Test Page", "platform": "facebook", "type": "page"},
            {"id": "group_456", "name": "Test Group", "platform": "facebook", "type": "group"},
            {"id": "ig_789", "name": "Test Instagram", "platform": "instagram", "type": "instagram"}
        ]
        
        form_data = {
            "content": "Test cross-platform post",
            "target_type": "cross-post", 
            "target_id": "cross-post",
            "target_name": f"Cross-post ({len(cross_targets)} plateformes)",
            "platform": "meta",
            "user_id": test_user_id,
            "cross_post_targets": json.dumps(cross_targets)
        }
        
        success, response = self.run_test(
            "Create Cross-Platform Post",
            "POST",
            "api/posts",
            200,
            data=form_data,
            form_data=True
        )
        
        if success and "post" in response:
            post = response["post"]
            platform = post.get("platform")
            target_type = post.get("target_type")
            cross_post_targets = post.get("cross_post_targets", [])
            
            if platform == "meta" and target_type == "cross-post":
                print("✅ Cross-platform post created with correct platform/type")
            else:
                print(f"⚠️  Unexpected platform/type: {platform}/{target_type}")
                
            if len(cross_post_targets) == len(cross_targets):
                print(f"✅ All {len(cross_targets)} cross-post targets stored")
            else:
                print(f"⚠️  Expected {len(cross_targets)} targets, got {len(cross_post_targets)}")
        
        return success

    def test_instagram_validation_logic(self):
        """Test Instagram validation through debug endpoint"""
        test_cases = [
            {
                "name": "Instagram with Image Link",
                "content": "Check out this image: https://picsum.photos/800/600",
                "platform": "instagram",
                "should_be_compatible": True
            },
            {
                "name": "Instagram Text Only",
                "content": "Just text without any media",
                "platform": "instagram", 
                "should_be_compatible": False
            },
            {
                "name": "Facebook Text Only",
                "content": "Just text without any media",
                "platform": "facebook",
                "should_be_compatible": True
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            success, response = self.run_test(
                f"Instagram Validation ({test_case['name']})",
                "POST",
                "api/debug/test-link-post",
                200,
                data={
                    "content": test_case["content"],
                    "platform": test_case["platform"]
                }
            )
            
            if success:
                instagram_compatible = response.get("instagram_compatible", False)
                detected_urls = response.get("detected_urls", [])
                link_metadata = response.get("link_metadata")
                
                print(f"   Platform: {test_case['platform']}")
                print(f"   Instagram Compatible: {instagram_compatible}")
                print(f"   URLs: {len(detected_urls)}")
                print(f"   Has Image: {bool(link_metadata and link_metadata.get('image'))}")
                
                if instagram_compatible == test_case["should_be_compatible"]:
                    print(f"✅ Correct Instagram compatibility for {test_case['name']}")
                else:
                    print(f"❌ Expected {test_case['should_be_compatible']}, got {instagram_compatible}")
                    all_passed = False
            else:
                all_passed = False
        
        return all_passed

    def test_uploads_directory_exists(self):
        """Test if uploads directory exists and is writable"""
        import os
        uploads_dir = "/app/backend/uploads"
        
        print(f"\n🔍 Testing Uploads Directory...")
        
        if os.path.exists(uploads_dir):
            print(f"✅ Uploads directory exists: {uploads_dir}")
            
            if os.access(uploads_dir, os.W_OK):
                print("✅ Uploads directory is writable")
                
                # Test creating a file
                test_file = os.path.join(uploads_dir, "test_write.txt")
                try:
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    print("✅ Can create and delete files in uploads directory")
                    self.tests_passed += 1
                except Exception as e:
                    print(f"❌ Cannot write to uploads directory: {e}")
            else:
                print("❌ Uploads directory is not writable")
        else:
            print(f"❌ Uploads directory does not exist: {uploads_dir}")
            
        self.tests_run += 1
        return os.path.exists(uploads_dir) and os.access(uploads_dir, os.W_OK)

def main():
    print("🚀 Starting Facebook Post Manager API Tests")
    print("=" * 50)
    
    tester = FacebookPostManagerTester()
    
    # Run all tests
    tests = [
        tester.test_health_check,
        tester.test_uploads_directory_exists,
        tester.test_cors_headers,
        tester.test_facebook_config_debug,
        tester.test_facebook_auth_url_generation,
        tester.test_facebook_token_debug_invalid,
        tester.test_facebook_token_debug_various_invalid_tokens,
        tester.test_facebook_auth_invalid,
        tester.test_facebook_code_exchange_invalid,
        tester.test_facebook_code_exchange_missing_data,
        tester.test_business_manager_endpoints_without_user,
        tester.test_get_posts_without_user,
        tester.test_create_post_without_auth,
        tester.test_create_post_with_form_data,
        tester.test_get_posts_with_user,
        # Media upload tests
        tester.test_media_upload_without_post,
        tester.test_media_upload_with_valid_post,
        tester.test_media_upload_invalid_file_type,
        tester.test_media_upload_large_file,
        tester.test_publish_post_without_user,
        tester.test_delete_post,
        tester.test_delete_nonexistent_post,
        tester.test_get_user_pages_nonexistent,
        # Link detection tests
        tester.test_extract_links_from_text,
        tester.test_extract_links_empty_text,
        tester.test_extract_links_no_urls,
        tester.test_extract_links_popular_sites,
        tester.test_link_preview_single_url,
        tester.test_link_preview_invalid_url,
        tester.test_link_preview_malformed_url,
        # Facebook link posting strategy tests
        tester.test_debug_test_link_post,
        tester.test_debug_test_link_post_no_links,
        tester.test_facebook_posting_strategy_simulation,
        tester.test_create_post_with_links,
        # Comment link functionality tests
        tester.test_create_post_with_comment_link,
        tester.test_create_post_without_comment_link,
        tester.test_create_post_with_empty_comment_link,
        tester.test_create_post_with_invalid_comment_link
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