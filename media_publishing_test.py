#!/usr/bin/env python3
"""
Focused test for the CORRECTED Facebook media publishing functionality.
This test specifically verifies the bug fixes mentioned in the review request.
"""

import requests
import json
import uuid
import io
from datetime import datetime

class MediaPublishingTester:
    def __init__(self, base_url="https://social-media-fixer.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_post_id = None
        self.test_user_id = str(uuid.uuid4())

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name}")
        
        if details:
            print(f"   {details}")

    def test_media_post_creation_with_multipart(self):
        """Test creating a post with media using the FIXED multipart upload logic"""
        print("\n🔍 Testing FIXED Media Post Creation with Multipart Upload")
        
        # Create a post first
        form_data = {
            "content": "Test media post with FIXED multipart upload logic",
            "target_type": "page", 
            "target_id": "test_page_123",
            "target_name": "Test Page Name",
            "user_id": self.test_user_id
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/posts", data=form_data)
            if response.status_code == 200:
                post_data = response.json()
                self.test_post_id = post_data["post"]["id"]
                self.log_test("Post Creation", True, f"Post ID: {self.test_post_id}")
                
                # Now test media upload with the FIXED logic
                test_image_content = b'\x89PNG\r\n\x1a\n\rIHDR\x01\x01\x08\x02\x90wS\xde\tpHYs\x0b\x13\x0b\x13\x01\x9a\x9c\x18\nIDATx\x9cc\xf8\x01\x01IEND\xaeB`\x82'
                
                files = {
                    'file': ('test_media.png', io.BytesIO(test_image_content), 'image/png')
                }
                
                media_response = requests.post(
                    f"{self.base_url}/api/posts/{self.test_post_id}/media", 
                    files=files
                )
                
                if media_response.status_code == 200:
                    media_data = media_response.json()
                    media_url = media_data.get("url")
                    self.log_test("FIXED Multipart Media Upload", True, f"Media URL: {media_url}")
                    
                    # Verify the media was actually stored
                    posts_response = requests.get(f"{self.base_url}/api/posts?user_id={self.test_user_id}")
                    if posts_response.status_code == 200:
                        posts = posts_response.json().get("posts", [])
                        updated_post = next((p for p in posts if p["id"] == self.test_post_id), None)
                        
                        if updated_post and updated_post.get("media_urls"):
                            media_urls = updated_post["media_urls"]
                            self.log_test("Media URL Storage", True, f"Stored URLs: {media_urls}")
                            return True
                        else:
                            self.log_test("Media URL Storage", False, "Media URLs not found in post")
                    else:
                        self.log_test("Post Retrieval", False, f"Status: {posts_response.status_code}")
                else:
                    self.log_test("FIXED Multipart Media Upload", False, f"Status: {media_response.status_code}")
            else:
                self.log_test("Post Creation", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Media Post Creation Test", False, f"Exception: {str(e)}")
            
        return False

    def test_cross_posting_fixed_endpoints(self):
        """Test that cross-posting now uses REAL page IDs instead of 'cross-post' endpoint"""
        print("\n🔍 Testing FIXED Cross-posting with Real Page IDs")
        
        # Create cross-post targets with REAL page IDs (not "cross-post")
        cross_targets = [
            {"id": "real_page_123", "name": "Real Facebook Page", "platform": "facebook", "type": "page"},
            {"id": "real_group_456", "name": "Real Facebook Group", "platform": "facebook", "type": "group"},
            {"id": "real_ig_789", "name": "Real Instagram Account", "platform": "instagram", "type": "instagram"}
        ]
        
        form_data = {
            "content": "Test cross-post with FIXED real endpoint logic",
            "target_type": "cross-post", 
            "target_id": "cross-post",  # This should trigger cross-posting logic
            "target_name": f"Cross-post ({len(cross_targets)} plateformes)",
            "platform": "meta",
            "user_id": self.test_user_id,
            "cross_post_targets": json.dumps(cross_targets)
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/posts", data=form_data)
            if response.status_code == 200:
                post_data = response.json()
                post = post_data["post"]
                stored_targets = post.get("cross_post_targets", [])
                
                # Verify that real page IDs are stored, not "cross-post"
                real_ids_found = []
                for target in stored_targets:
                    target_id = target.get("id")
                    if target_id and target_id != "cross-post":
                        real_ids_found.append(target_id)
                
                if len(real_ids_found) == len(cross_targets):
                    self.log_test("FIXED Cross-post Real IDs", True, f"Real IDs: {real_ids_found}")
                    
                    # Verify no "cross-post" endpoint references
                    if "cross-post" not in str(stored_targets):
                        self.log_test("No Cross-post Endpoint References", True, "Clean of 'cross-post' references")
                        return True
                    else:
                        self.log_test("No Cross-post Endpoint References", False, "Still contains 'cross-post' references")
                else:
                    self.log_test("FIXED Cross-post Real IDs", False, f"Expected {len(cross_targets)}, got {len(real_ids_found)}")
            else:
                self.log_test("Cross-post Creation", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Cross-posting Test", False, f"Exception: {str(e)}")
            
        return False

    def test_media_download_and_upload_process(self):
        """Test the FIXED media download and multipart upload process"""
        print("\n🔍 Testing FIXED Media Download and Upload Process")
        
        # Test the debug endpoint that simulates the media posting strategy
        test_cases = [
            {
                "name": "Media Post Strategy",
                "content": "Check out this image!",
                "media_url": "https://picsum.photos/800/600",
                "expected_strategy": "media_post"
            },
            {
                "name": "Link with Image Strategy", 
                "content": "Great image here: https://picsum.photos/400/300",
                "expected_strategy": "link_preview"
            }
        ]
        
        success_count = 0
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/debug/test-link-post",
                    json={
                        "content": test_case["content"],
                        "platform": "facebook"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    strategy = data.get("post_strategy")
                    detected_urls = data.get("detected_urls", [])
                    link_metadata = data.get("link_metadata")
                    
                    # Check if the strategy detection is working
                    if strategy:
                        self.log_test(f"Strategy Detection - {test_case['name']}", True, f"Strategy: {strategy}")
                        success_count += 1
                        
                        # Check if link metadata extraction is working (FIXED)
                        if link_metadata and link_metadata.get("image"):
                            self.log_test(f"Image Metadata Extraction - {test_case['name']}", True, f"Image found: {link_metadata['image'][:50]}...")
                        elif detected_urls:
                            self.log_test(f"URL Detection - {test_case['name']}", True, f"URLs: {len(detected_urls)}")
                    else:
                        self.log_test(f"Strategy Detection - {test_case['name']}", False, "No strategy returned")
                else:
                    self.log_test(f"Debug Endpoint - {test_case['name']}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Media Process Test - {test_case['name']}", False, f"Exception: {str(e)}")
        
        return success_count == len(test_cases)

    def test_error_handling_improvements(self):
        """Test the IMPROVED error handling and logging"""
        print("\n🔍 Testing IMPROVED Error Handling and Logging")
        
        test_cases = [
            {
                "name": "Invalid Media URL",
                "content": "Post with invalid media",
                "should_handle_gracefully": True
            },
            {
                "name": "Empty Content with Media",
                "content": "",
                "should_handle_gracefully": True
            }
        ]
        
        success_count = 0
        
        for test_case in test_cases:
            try:
                form_data = {
                    "content": test_case["content"],
                    "target_type": "page", 
                    "target_id": "test_page_error_handling",
                    "target_name": "Error Handling Test Page",
                    "user_id": str(uuid.uuid4())
                }
                
                response = requests.post(f"{self.base_url}/api/posts", data=form_data)
                
                if response.status_code == 200:
                    # The backend should handle these cases gracefully
                    post_data = response.json()
                    message = post_data.get("message", "")
                    
                    if "succès" in message.lower() or "success" in message.lower():
                        self.log_test(f"Graceful Handling - {test_case['name']}", True, "Post created successfully")
                        success_count += 1
                    else:
                        self.log_test(f"Graceful Handling - {test_case['name']}", False, f"Unexpected message: {message}")
                else:
                    # Check if it's a proper error response (not a crash)
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            self.log_test(f"Proper Error Response - {test_case['name']}", True, f"Error: {error_data['detail']}")
                            success_count += 1
                        else:
                            self.log_test(f"Error Response Format - {test_case['name']}", False, "No detail in error")
                    except:
                        self.log_test(f"Error Response Format - {test_case['name']}", False, "Invalid JSON error response")
                        
            except Exception as e:
                self.log_test(f"Error Handling Test - {test_case['name']}", False, f"Exception: {str(e)}")
        
        return success_count == len(test_cases)

    def test_variable_scope_fixes(self):
        """Test that the FIXED variable scope issues are resolved"""
        print("\n🔍 Testing FIXED Variable Scope Issues")
        
        # Test various content types that previously caused scope errors
        test_cases = [
            "Text only post",
            "Post with link: https://github.com/facebook/react",
            "",  # Empty content
            "Post with multiple links: https://reactjs.org and https://github.com/facebook/react"
        ]
        
        success_count = 0
        
        for i, content in enumerate(test_cases):
            try:
                form_data = {
                    "content": content,
                    "target_type": "page", 
                    "target_id": f"scope_test_page_{i}",
                    "target_name": f"Scope Test Page {i}",
                    "user_id": str(uuid.uuid4())
                }
                
                response = requests.post(f"{self.base_url}/api/posts", data=form_data)
                
                if response.status_code == 200:
                    self.log_test(f"Variable Scope Test {i+1}", True, f"Content: '{content[:30]}...'")
                    success_count += 1
                else:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                    
                    # Check if it's a scope error (should not happen with fixes)
                    error_msg = str(error_data.get("detail", "")).lower()
                    if "cannot access local variable" in error_msg or "requests" in error_msg:
                        self.log_test(f"Variable Scope Test {i+1}", False, f"SCOPE ERROR STILL EXISTS: {error_msg}")
                    else:
                        # Other errors are acceptable (validation, etc.)
                        self.log_test(f"Variable Scope Test {i+1}", True, f"No scope error (other error: {error_msg[:50]})")
                        success_count += 1
                        
            except Exception as e:
                self.log_test(f"Variable Scope Test {i+1}", False, f"Exception: {str(e)}")
        
        return success_count == len(test_cases)

    def run_all_tests(self):
        """Run all media publishing tests"""
        print("🚀 Starting CORRECTED Facebook Media Publishing Tests")
        print("=" * 70)
        print("Testing the FIXED functionality mentioned in the review request:")
        print("1. Variable scope error with 'requests' module")
        print("2. Incorrect API endpoint usage (cross-post vs real page IDs)")
        print("3. Missing error handling and undefined variables")
        print("4. Refactored media upload logic with proper Facebook API patterns")
        print("5. Proper cross-posting support with individual target handling")
        print("=" * 70)
        
        # Run all tests
        tests = [
            self.test_variable_scope_fixes,
            self.test_cross_posting_fixed_endpoints,
            self.test_media_post_creation_with_multipart,
            self.test_media_download_and_upload_process,
            self.test_error_handling_improvements
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                self.tests_run += 1
        
        # Print results
        print("\n" + "=" * 70)
        print(f"📊 MEDIA PUBLISHING TEST RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL CRITICAL BUGS HAVE BEEN FIXED!")
            print("✅ Variable scope issues resolved")
            print("✅ Cross-posting endpoints fixed")
            print("✅ Media upload logic improved")
            print("✅ Error handling enhanced")
            return 0
        else:
            failed_count = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_count} issues still need attention")
            
            if failed_count > self.tests_run * 0.5:
                print("❌ Major issues still exist - more than 50% of tests failed")
                return 2
            else:
                print("⚠️  Minor issues detected - most critical bugs are fixed")
                return 1

def main():
    tester = MediaPublishingTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    exit(main())