#!/usr/bin/env python3
"""
Backend Test Suite for Gizmobbs Webhook Functionality
Testing the fixes for parameter mismatch and facebook_post_data UnboundLocalError
"""

import requests
import json
import sys
import tempfile
import os
from datetime import datetime
from io import BytesIO
from PIL import Image

class WebhookTester:
    def __init__(self, base_url="https://video-post-feature.preview.emergentagent.com"):
        self.base_url = base_url.rstrip('/')
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []

    def log_test(self, name, success, message="", details=None):
        """Log test results"""
        self.tests_run += 1
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n{status} - {name}")
        if message:
            print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        
        if success:
            self.tests_passed += 1
        else:
            self.errors.append(f"{name}: {message}")

    def create_test_image(self):
        """Create a test image for webhook testing"""
        # Create a simple test image
        img = Image.new('RGB', (800, 600), color='lightblue')
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        img.save(temp_file.name, 'JPEG', quality=90)
        temp_file.close()
        
        return temp_file.name

    def test_health_check(self):
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Backend is running - Status: {data.get('status', 'unknown')}"
                )
                
                # Check MongoDB connection
                if data.get('mongodb') == 'connected':
                    self.log_test("MongoDB Connection", True, "Database connected successfully")
                else:
                    self.log_test("MongoDB Connection", False, f"Database status: {data.get('mongodb')}")
                
                return True
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_webhook_endpoint_info(self):
        """Test the webhook info endpoint (GET)"""
        try:
            response = requests.get(f"{self.base_url}/api/webhook", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Webhook Info Endpoint", 
                    True, 
                    f"Webhook info retrieved - Available stores: {len(data.get('available_stores', []))}"
                )
                return True
            else:
                self.log_test("Webhook Info Endpoint", False, f"HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_test("Webhook Info Endpoint", False, f"Error: {str(e)}")
            return False

    def test_webhook_bug_fixes(self):
        """Test the main webhook functionality with the bug fix payload"""
        print(f"\n🧪 Testing Webhook Bug Fixes...")
        print("=" * 60)
        
        # Create test image
        test_image_path = self.create_test_image()
        
        try:
            # Prepare the test payload as specified in the request
            test_payload = {
                "title": "Test Product for Bug Fix Verification",
                "description": "Testing the facebook_post_data fix",
                "url": "https://example.com/test-product",
                "store": "gizmobbs",
                "image_url": "https://via.placeholder.com/800x600/CCCCCC/000000.jpg?text=Test+Image"
            }
            
            # Prepare multipart form data
            with open(test_image_path, 'rb') as img_file:
                files = {
                    'image': ('test_image.jpg', img_file, 'image/jpeg')
                }
                data = {
                    'json_data': json.dumps(test_payload)
                }
                
                print(f"📤 Sending webhook request...")
                print(f"   Store: {test_payload['store']}")
                print(f"   Title: {test_payload['title']}")
                
                response = requests.post(
                    f"{self.base_url}/api/webhook",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            print(f"📥 Response Status: {response.status_code}")
            
            # Test 1: No server crashes (should not return 500)
            if response.status_code == 500:
                self.log_test(
                    "No Server Crashes", 
                    False, 
                    "Server returned 500 - Bug fixes may not be working",
                    response.text[:200]
                )
                return False
            else:
                self.log_test(
                    "No Server Crashes", 
                    True, 
                    f"Server handled request without crashing (HTTP {response.status_code})"
                )
            
            # Test 2: Valid JSON response
            try:
                response_data = response.json()
                self.log_test("Valid JSON Response", True, "Response is valid JSON")
            except json.JSONDecodeError:
                self.log_test("Valid JSON Response", False, "Response is not valid JSON")
                return False
            
            # Test 3: Check for publication_results in response
            if 'data' in response_data and 'publication_results' in response_data['data']:
                publication_results = response_data['data']['publication_results']
                self.log_test(
                    "Publication Results Present", 
                    True, 
                    f"Found {len(publication_results)} publication result(s)"
                )
                
                # Test 4: Check that results don't contain parameter mismatch errors
                has_param_error = False
                has_facebook_data_error = False
                
                for result in publication_results:
                    result_str = str(result).lower()
                    if 'parameter' in result_str and 'mismatch' in result_str:
                        has_param_error = True
                    if 'facebook_post_data' in result_str and ('unbound' in result_str or 'not defined' in result_str):
                        has_facebook_data_error = True
                
                self.log_test(
                    "No Parameter Mismatch Errors", 
                    not has_param_error, 
                    "Parameter mismatch error not found" if not has_param_error else "Parameter mismatch error detected"
                )
                
                self.log_test(
                    "No facebook_post_data UnboundLocalError", 
                    not has_facebook_data_error, 
                    "facebook_post_data error not found" if not has_facebook_data_error else "facebook_post_data UnboundLocalError detected"
                )
                
                # Test 5: Check publication status
                for i, result in enumerate(publication_results):
                    status = result.get('status', 'unknown')
                    message = result.get('message', 'No message')
                    platforms = result.get('platforms', [])
                    
                    print(f"\n   Publication Result {i+1}:")
                    print(f"   Status: {status}")
                    print(f"   Message: {message}")
                    print(f"   Platforms: {len(platforms)} platform(s)")
                    
                    # Check for graceful Instagram failure handling
                    instagram_handled_gracefully = True
                    facebook_status = "unknown"
                    
                    for platform in platforms:
                        platform_name = platform.get('platform', 'unknown')
                        platform_status = platform.get('status', 'unknown')
                        
                        if platform_name == 'instagram':
                            # Instagram may fail due to API access issues - should be handled gracefully
                            if platform_status == 'error':
                                error_msg = platform.get('error', '').lower()
                                if 'api' in error_msg or 'access' in error_msg or 'domain' in error_msg:
                                    print(f"   ✅ Instagram failure handled gracefully: {platform.get('error', 'Unknown error')}")
                                else:
                                    instagram_handled_gracefully = False
                        elif platform_name == 'facebook':
                            facebook_status = platform_status
                    
                    self.log_test(
                        f"Instagram Error Handling (Result {i+1})", 
                        instagram_handled_gracefully, 
                        "Instagram errors handled gracefully" if instagram_handled_gracefully else "Instagram errors not handled properly"
                    )
                    
                    # Facebook should show proper status
                    if facebook_status != "unknown":
                        self.log_test(
                            f"Facebook Status Available (Result {i+1})", 
                            True, 
                            f"Facebook status: {facebook_status}"
                        )
                    
            else:
                self.log_test(
                    "Publication Results Present", 
                    False, 
                    "No publication_results found in response"
                )
            
            # Test 6: Check response structure
            expected_fields = ['status', 'message', 'data']
            missing_fields = [field for field in expected_fields if field not in response_data]
            
            self.log_test(
                "Response Structure", 
                len(missing_fields) == 0, 
                f"All expected fields present" if len(missing_fields) == 0 else f"Missing fields: {missing_fields}"
            )
            
            # Print full response for debugging
            print(f"\n📋 Full Response Data:")
            print(json.dumps(response_data, indent=2)[:1000] + "..." if len(str(response_data)) > 1000 else json.dumps(response_data, indent=2))
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_test("Webhook Request", False, f"Request failed: {str(e)}")
            return False
        except Exception as e:
            self.log_test("Webhook Test", False, f"Unexpected error: {str(e)}")
            return False
        finally:
            # Clean up test image
            try:
                os.unlink(test_image_path)
            except:
                pass

    def test_webhook_without_store(self):
        """Test webhook without store parameter (should not crash)"""
        test_image_path = self.create_test_image()
        
        try:
            # Test payload without store
            test_payload = {
                "title": "Test Product Without Store",
                "description": "Testing webhook without store parameter",
                "url": "https://example.com/test-product-no-store"
                # No store parameter
            }
            
            with open(test_image_path, 'rb') as img_file:
                files = {
                    'image': ('test_image.jpg', img_file, 'image/jpeg')
                }
                data = {
                    'json_data': json.dumps(test_payload)
                }
                
                response = requests.post(
                    f"{self.base_url}/api/webhook",
                    files=files,
                    data=data,
                    timeout=15
                )
            
            # Should not crash even without store
            if response.status_code != 500:
                self.log_test(
                    "Webhook Without Store", 
                    True, 
                    f"Handled request without store parameter (HTTP {response.status_code})"
                )
                return True
            else:
                self.log_test("Webhook Without Store", False, "Server crashed without store parameter")
                return False
                
        except Exception as e:
            self.log_test("Webhook Without Store", False, f"Error: {str(e)}")
            return False
        finally:
            try:
                os.unlink(test_image_path)
            except:
                pass

    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🚀 Starting Gizmobbs Webhook Bug Fix Tests")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Time: {datetime.now().isoformat()}")
        
        # Run tests
        self.test_health_check()
        self.test_webhook_endpoint_info()
        self.test_webhook_bug_fixes()
        self.test_webhook_without_store()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.errors:
            print(f"\n❌ FAILED TESTS:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.tests_passed == self.tests_run:
            print(f"\n🎉 ALL TESTS PASSED! Bug fixes are working correctly.")
            return 0
        else:
            print(f"\n⚠️  Some tests failed. Check the details above.")
            return 1

def main():
    """Main test execution"""
    tester = WebhookTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())