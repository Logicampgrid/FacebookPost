#!/usr/bin/env python3
"""
Specific test for Facebook media posting functionality
Testing the issue mentioned by the user about media posting
"""

import requests
import json
import uuid
import io
from datetime import datetime

class MediaPostingTester:
    def __init__(self, base_url="https://just-ok-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.test_user_id = str(uuid.uuid4())
        self.test_post_id = None
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def test_media_url_access(self):
        """Test accessing media URLs directly"""
        self.log("🔍 Testing media URL access...")
        
        # Test the specific URL mentioned by user
        problematic_url = "https://just-ok-3.preview.emergentagent.com/uploads/d2928827-e813-46fd-bb1c-246278aab168.jpg"
        
        try:
            response = requests.head(problematic_url)
            self.log(f"   Problematic URL status: {response.status_code}")
            if response.status_code == 404:
                self.log("   ✅ Expected 404 - file doesn't exist (as mentioned by user)")
            else:
                self.log(f"   ⚠️  Unexpected status: {response.status_code}")
        except Exception as e:
            self.log(f"   ❌ Error accessing URL: {e}")
            
        # Test uploads directory
        uploads_dir_url = "https://just-ok-3.preview.emergentagent.com/uploads/"
        try:
            response = requests.head(uploads_dir_url)
            self.log(f"   Uploads directory status: {response.status_code}")
            if response.status_code == 404:
                self.log("   ⚠️  Uploads directory not accessible - this might be a routing issue")
            else:
                self.log(f"   ✅ Uploads directory accessible: {response.status_code}")
        except Exception as e:
            self.log(f"   ❌ Error accessing uploads directory: {e}")
    
    def test_create_post_with_media_flow(self):
        """Test the complete flow: create post -> upload media -> check URLs"""
        self.log("🔍 Testing complete media posting flow...")
        
        # Step 1: Create a post
        form_data = {
            "content": "Test post with media for Facebook posting",
            "target_type": "page", 
            "target_id": "test_page_facebook_123",
            "target_name": "Test Facebook Page",
            "platform": "facebook",
            "user_id": self.test_user_id
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/posts", data=form_data)
            if response.status_code == 200:
                post_data = response.json()
                self.test_post_id = post_data["post"]["id"]
                self.log(f"   ✅ Post created: {self.test_post_id}")
            else:
                self.log(f"   ❌ Failed to create post: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"   ❌ Error creating post: {e}")
            return False
            
        # Step 2: Upload media to the post
        test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01IEND\xaeB`\x82'
        
        files = {
            'file': ('facebook_test_media.png', io.BytesIO(test_image_content), 'image/png')
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/posts/{self.test_post_id}/media", files=files)
            if response.status_code == 200:
                media_data = response.json()
                media_url = media_data.get("url")
                self.log(f"   ✅ Media uploaded: {media_url}")
                
                # Step 3: Test if the uploaded media is accessible
                full_media_url = f"{self.base_url}{media_url}"
                media_response = requests.head(full_media_url)
                self.log(f"   Media accessibility: {media_response.status_code}")
                
                if media_response.status_code == 200:
                    self.log("   ✅ Uploaded media is accessible")
                else:
                    self.log(f"   ❌ Uploaded media not accessible: {media_response.status_code}")
                    
                return media_url
            else:
                self.log(f"   ❌ Failed to upload media: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"   ❌ Error uploading media: {e}")
            return False
    
    def test_facebook_posting_strategy_with_media(self, media_url):
        """Test Facebook posting strategy with uploaded media"""
        self.log("🔍 Testing Facebook posting strategy with media...")
        
        # Get the updated post to see media_urls
        try:
            response = requests.get(f"{self.base_url}/api/posts?user_id={self.test_user_id}")
            if response.status_code == 200:
                posts_data = response.json()
                posts = posts_data.get("posts", [])
                
                # Find our test post
                test_post = None
                for post in posts:
                    if post["id"] == self.test_post_id:
                        test_post = post
                        break
                
                if test_post:
                    media_urls = test_post.get("media_urls", [])
                    content = test_post.get("content", "")
                    
                    self.log(f"   Post content: {content}")
                    self.log(f"   Media URLs: {media_urls}")
                    
                    if len(media_urls) > 0:
                        self.log("   ✅ Media URLs stored in post")
                        
                        # Test the Facebook posting logic simulation
                        self.log("   🔍 Testing Facebook posting logic...")
                        
                        # Simulate what happens in post_to_facebook function
                        media_url_from_post = media_urls[0]
                        
                        if media_url_from_post.startswith('http'):
                            full_media_url = media_url_from_post
                        else:
                            # This is the logic from the backend
                            full_media_url = f"http://localhost:8001{media_url_from_post}"
                            
                        self.log(f"   Facebook would try to access: {full_media_url}")
                        
                        # This is the issue! The backend constructs localhost URLs
                        # but the actual server is running on the public domain
                        if "localhost:8001" in full_media_url:
                            self.log("   ❌ ISSUE FOUND: Backend constructs localhost URLs!")
                            self.log("   ❌ Facebook API cannot access localhost URLs from external servers")
                            
                            # Test what the correct URL should be
                            correct_url = full_media_url.replace("http://localhost:8001", self.base_url)
                            self.log(f"   ✅ Correct URL should be: {correct_url}")
                            
                            # Test if correct URL works
                            correct_response = requests.head(correct_url)
                            if correct_response.status_code == 200:
                                self.log("   ✅ Correct URL is accessible")
                            else:
                                self.log(f"   ❌ Even correct URL fails: {correct_response.status_code}")
                        else:
                            self.log("   ✅ Media URL looks correct")
                    else:
                        self.log("   ❌ No media URLs found in post")
                else:
                    self.log("   ❌ Test post not found")
            else:
                self.log(f"   ❌ Failed to get posts: {response.status_code}")
        except Exception as e:
            self.log(f"   ❌ Error testing posting strategy: {e}")
    
    def test_facebook_posting_simulation(self):
        """Simulate Facebook posting without actually posting"""
        self.log("🔍 Testing Facebook posting simulation...")
        
        if not self.test_post_id:
            self.log("   ⚠️  No test post available")
            return
            
        # This would normally require a real Facebook token
        # But we can test the logic without actually posting
        
        try:
            # Try to publish the post (this will fail due to no real user/token)
            response = requests.post(f"{self.base_url}/api/posts/{self.test_post_id}/publish")
            
            self.log(f"   Publish attempt status: {response.status_code}")
            
            if response.status_code == 500:
                error_data = response.json()
                error_detail = error_data.get("detail", "")
                
                if "User not found" in error_detail:
                    self.log("   ✅ Expected error: User not found (no real Facebook auth)")
                else:
                    self.log(f"   ⚠️  Unexpected error: {error_detail}")
            else:
                self.log(f"   ⚠️  Unexpected response: {response.status_code}")
                
        except Exception as e:
            self.log(f"   ❌ Error in publish simulation: {e}")
    
    def test_debug_endpoints(self):
        """Test debug endpoints for Facebook configuration"""
        self.log("🔍 Testing debug endpoints...")
        
        # Test Facebook config
        try:
            response = requests.get(f"{self.base_url}/api/debug/facebook-config")
            if response.status_code == 200:
                config = response.json()
                self.log(f"   Facebook App ID: {config.get('app_id')}")
                self.log(f"   Graph URL: {config.get('graph_url')}")
                self.log(f"   App Secret configured: {config.get('app_secret_configured')}")
                
                if config.get('app_id') == '5664227323683118':
                    self.log("   ✅ Facebook App ID is correct")
                else:
                    self.log("   ❌ Facebook App ID mismatch")
            else:
                self.log(f"   ❌ Failed to get Facebook config: {response.status_code}")
        except Exception as e:
            self.log(f"   ❌ Error getting Facebook config: {e}")
            
        # Test with test token
        try:
            response = requests.get(f"{self.base_url}/api/debug/facebook-token/test_token_123")
            if response.status_code == 200:
                token_data = response.json()
                status = token_data.get("status")
                if status == "invalid":
                    self.log("   ✅ Test token correctly identified as invalid")
                else:
                    self.log(f"   ⚠️  Unexpected token status: {status}")
            else:
                self.log(f"   ❌ Failed to test token: {response.status_code}")
        except Exception as e:
            self.log(f"   ❌ Error testing token: {e}")
    
    def run_all_tests(self):
        """Run all media posting tests"""
        self.log("🚀 Starting Media Posting Tests for Facebook")
        self.log("=" * 60)
        
        # Test 1: Media URL access
        self.test_media_url_access()
        
        # Test 2: Complete media posting flow
        media_url = self.test_create_post_with_media_flow()
        
        # Test 3: Facebook posting strategy
        if media_url:
            self.test_facebook_posting_strategy_with_media(media_url)
        
        # Test 4: Publishing simulation
        self.test_facebook_posting_simulation()
        
        # Test 5: Debug endpoints
        self.test_debug_endpoints()
        
        self.log("=" * 60)
        self.log("🏁 Media Posting Tests Completed")

if __name__ == "__main__":
    tester = MediaPostingTester()
    tester.run_all_tests()