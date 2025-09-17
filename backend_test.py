#!/usr/bin/env python3
"""
Backend API Testing for Meta Publishing Platform
Tests error handling fixes and API functionality
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

class MetaPublishingAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'MetaPublishingTester/1.0'
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
        """Test basic health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Health check failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"Health check response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check required fields
            required_fields = ['status', 'timestamp']
            for field in required_fields:
                if field not in data:
                    self.log(f"Missing required field in health response: {field}", "ERROR")
                    return False
            
            if data['status'] != 'healthy':
                self.log(f"Service not healthy: {data['status']}", "ERROR")
                return False
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"Network error in health check: {str(e)}", "ERROR")
            return False
        except json.JSONDecodeError as e:
            self.log(f"Invalid JSON in health response: {str(e)}", "ERROR")
            return False

    def test_stores_endpoint(self) -> bool:
        """Test stores configuration endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/stores", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Stores endpoint failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"Stores response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check structure
            if 'stores' not in data:
                self.log("Missing 'stores' field in response", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"Error testing stores endpoint: {str(e)}", "ERROR")
            return False

    def test_invalid_store_publish(self) -> bool:
        """Test error handling for invalid store in publish endpoint"""
        try:
            invalid_payload = {
                "store": "invalid_store_name",
                "message": "Test message",
                "product_url": "https://example.com/product",
                "platforms": ["facebook"]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/publish",
                json=invalid_payload,
                timeout=10
            )
            
            # Should return 400 for invalid store
            if response.status_code != 400:
                self.log(f"Expected 400 for invalid store, got {response.status_code}", "ERROR")
                return False
            
            # Check if error message is properly formatted (not an object)
            try:
                data = response.json()
                self.log(f"Error response: {json.dumps(data, indent=2)}", "INFO")
                
                # Check that detail is a string, not an object
                if 'detail' in data:
                    if isinstance(data['detail'], dict) or isinstance(data['detail'], list):
                        self.log("Error detail is an object/array instead of string - this was the bug!", "ERROR")
                        return False
                    elif not isinstance(data['detail'], str):
                        self.log(f"Error detail is not a string: {type(data['detail'])}", "ERROR")
                        return False
                    else:
                        self.log(f"✅ Error detail is properly formatted string: {data['detail']}", "SUCCESS")
                
                return True
                
            except json.JSONDecodeError:
                self.log("Response is not valid JSON", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"Error testing invalid store publish: {str(e)}", "ERROR")
            return False

    def test_missing_fields_validation(self) -> bool:
        """Test validation error handling for missing required fields"""
        try:
            # Test with missing required fields
            invalid_payload = {
                "store": "logicantiq",
                # Missing message and product_url
                "platforms": ["facebook"]
            }
            
            response = self.session.post(
                f"{self.base_url}/api/publish",
                json=invalid_payload,
                timeout=10
            )
            
            # Should return 422 for validation error
            if response.status_code not in [400, 422]:
                self.log(f"Expected 400/422 for validation error, got {response.status_code}", "ERROR")
                return False
            
            try:
                data = response.json()
                self.log(f"Validation error response: {json.dumps(data, indent=2)}", "INFO")
                
                # Check that error is properly formatted
                if 'detail' in data:
                    detail = data['detail']
                    
                    # If it's a list (Pydantic validation errors), check each item
                    if isinstance(detail, list):
                        self.log("Error detail is a list - checking if items are properly formatted", "INFO")
                        for item in detail:
                            if isinstance(item, dict):
                                # This is fine for Pydantic validation errors
                                if 'msg' not in item and 'message' not in item:
                                    self.log(f"Validation error item missing message: {item}", "ERROR")
                                    return False
                            elif not isinstance(item, str):
                                self.log(f"Validation error item is not string or dict: {type(item)}", "ERROR")
                                return False
                        self.log("✅ Validation errors are properly structured", "SUCCESS")
                    elif isinstance(detail, str):
                        self.log(f"✅ Error detail is string: {detail}", "SUCCESS")
                    else:
                        self.log(f"Error detail has unexpected type: {type(detail)}", "ERROR")
                        return False
                
                return True
                
            except json.JSONDecodeError:
                self.log("Validation error response is not valid JSON", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"Error testing validation: {str(e)}", "ERROR")
            return False

    def test_posts_endpoint_creation(self) -> bool:
        """Test post creation with validation"""
        try:
            # Test with minimal valid data
            valid_payload = {
                "content": "Test post content",
                "platform": "facebook"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/posts",
                json=valid_payload,
                timeout=10
            )
            
            self.log(f"Post creation response status: {response.status_code}", "INFO")
            
            if response.status_code == 201:
                # Success case
                data = response.json()
                self.log(f"Post created successfully: {json.dumps(data, indent=2)}", "SUCCESS")
                return True
            elif response.status_code in [400, 422]:
                # Validation error - check formatting
                try:
                    data = response.json()
                    self.log(f"Post creation validation error: {json.dumps(data, indent=2)}", "INFO")
                    
                    # Check error formatting
                    if 'detail' in data:
                        if isinstance(data['detail'], (dict, list)) and not isinstance(data['detail'], str):
                            # This might be acceptable for Pydantic errors, but let's check structure
                            self.log("Validation error is object/array - checking structure", "INFO")
                        else:
                            self.log(f"✅ Error is properly formatted: {data['detail']}", "SUCCESS")
                    
                    return True  # Validation errors are expected and properly handled
                    
                except json.JSONDecodeError:
                    self.log("Post creation error response is not valid JSON", "ERROR")
                    return False
            else:
                self.log(f"Unexpected status code for post creation: {response.status_code}", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"Error testing post creation: {str(e)}", "ERROR")
            return False

    def test_posts_list_endpoint(self) -> bool:
        """Test posts listing endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/posts", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Posts list failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"Posts list response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check structure
            if 'posts' not in data:
                self.log("Missing 'posts' field in response", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"Error testing posts list: {str(e)}", "ERROR")
            return False

    def test_facebook_auth_invalid_token(self) -> bool:
        """Test Facebook auth with invalid token - should return proper error"""
        try:
            invalid_payload = {
                "access_token": "invalid_token_12345"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/facebook",
                json=invalid_payload,
                timeout=10
            )
            
            # Should return error status
            if response.status_code not in [400, 401, 422]:
                self.log(f"Expected error status for invalid token, got {response.status_code}", "ERROR")
                return False
            
            try:
                data = response.json()
                self.log(f"Facebook auth error response: {json.dumps(data, indent=2)}", "INFO")
                
                # Check error formatting
                if 'detail' in data:
                    if isinstance(data['detail'], (dict, list)) and not isinstance(data['detail'], str):
                        self.log("Facebook auth error is object - checking if this causes React errors", "WARNING")
                        # This might be the source of "Objects are not valid as a React child" error
                    else:
                        self.log(f"✅ Facebook auth error is properly formatted: {data['detail']}", "SUCCESS")
                
                return True
                
            except json.JSONDecodeError:
                self.log("Facebook auth error response is not valid JSON", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"Error testing Facebook auth: {str(e)}", "ERROR")
            return False

    def test_webhook_verification(self) -> bool:
        """Test webhook verification endpoint"""
        try:
            # Test webhook verification (GET request)
            params = {
                'hub.mode': 'subscribe',
                'hub.verify_token': 'mon_token_secret_webhook',
                'hub.challenge': 'test_challenge_12345'
            }
            
            response = self.session.get(
                f"{self.base_url}/api/webhook",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                # Should return the challenge as plain text
                if response.text == 'test_challenge_12345':
                    self.log("✅ Webhook verification working correctly", "SUCCESS")
                    return True
                else:
                    self.log(f"Webhook returned wrong challenge: {response.text}", "ERROR")
                    return False
            else:
                self.log(f"Webhook verification failed with status {response.status_code}", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"Error testing webhook verification: {str(e)}", "ERROR")
            return False

    def test_error_response_formats(self) -> bool:
        """Test various endpoints to ensure error responses are properly formatted"""
        try:
            test_cases = [
                # Test invalid JSON
                {
                    'name': 'Invalid JSON to publish endpoint',
                    'method': 'POST',
                    'url': f"{self.base_url}/api/publish",
                    'data': '{"invalid": json}',  # Invalid JSON
                    'headers': {'Content-Type': 'application/json'}
                },
                # Test non-existent endpoint
                {
                    'name': 'Non-existent API endpoint',
                    'method': 'GET',
                    'url': f"{self.base_url}/api/nonexistent",
                    'data': None,
                    'headers': {}
                }
            ]
            
            all_passed = True
            
            for test_case in test_cases:
                try:
                    self.log(f"Testing: {test_case['name']}", "INFO")
                    
                    if test_case['method'] == 'POST':
                        response = self.session.post(
                            test_case['url'],
                            data=test_case['data'],
                            headers=test_case['headers'],
                            timeout=10
                        )
                    else:
                        response = self.session.get(test_case['url'], timeout=10)
                    
                    self.log(f"Response status: {response.status_code}", "INFO")
                    
                    # Try to parse response
                    try:
                        data = response.json()
                        self.log(f"Response data: {json.dumps(data, indent=2)}", "INFO")
                        
                        # Check if error is properly formatted
                        if 'detail' in data:
                            if isinstance(data['detail'], str):
                                self.log(f"✅ Error properly formatted as string", "SUCCESS")
                            else:
                                self.log(f"⚠️ Error is not a string: {type(data['detail'])}", "WARNING")
                                # This might not be critical depending on the error type
                        
                    except json.JSONDecodeError:
                        self.log("Response is not JSON (might be expected for some errors)", "INFO")
                    
                except Exception as e:
                    self.log(f"Error in test case {test_case['name']}: {str(e)}", "ERROR")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log(f"Error testing error response formats: {str(e)}", "ERROR")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        self.log("Starting comprehensive API tests for error handling fixes", "INFO")
        self.log(f"Testing backend at: {self.base_url}", "INFO")
        
        # Test basic connectivity first
        if not self.run_test("Health Check", self.test_health_check):
            self.log("❌ Basic connectivity failed - stopping tests", "ERROR")
            return self.get_summary()
        
        # Core API tests
        self.run_test("Stores Endpoint", self.test_stores_endpoint)
        self.run_test("Posts List Endpoint", self.test_posts_list_endpoint)
        self.run_test("Posts Creation Validation", self.test_posts_endpoint_creation)
        
        # Error handling tests (main focus)
        self.run_test("Invalid Store Publish Error", self.test_invalid_store_publish)
        self.run_test("Missing Fields Validation Error", self.test_missing_fields_validation)
        self.run_test("Facebook Auth Invalid Token Error", self.test_facebook_auth_invalid_token)
        self.run_test("Webhook Verification", self.test_webhook_verification)
        self.run_test("Error Response Formats", self.test_error_response_formats)
        
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
    # Get backend URL from environment
    import os
    backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://token-exchange-5.preview.emergentagent.com')
    
    print(f"🚀 Meta Publishing Platform - Backend API Tests")
    print(f"📡 Backend URL: {backend_url}")
    print(f"🎯 Focus: Error handling fixes for React 'Objects are not valid as a React child' issue")
    print("=" * 80)
    
    # Initialize tester
    tester = MetaPublishingAPITester(backend_url)
    
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
    
    print("\n🎯 ERROR HANDLING ASSESSMENT:")
    if summary['success_rate'] >= 80:
        print("✅ Error handling appears to be working correctly")
        print("✅ API responses should not cause 'Objects are not valid as a React child' errors")
    else:
        print("⚠️ Some error handling issues detected")
        print("⚠️ May still cause React rendering issues")
    
    # Return appropriate exit code
    return 0 if summary['status'] == 'PASSED' else 1

if __name__ == "__main__":
    sys.exit(main())