#!/usr/bin/env python3
"""
Backend API Test Suite for Meta Publishing Platform
Tests the corrected FastAPI backend on port 8001
"""

import requests
import sys
import json
import io
import tempfile
import os
from datetime import datetime

class MetaPublishingTester:
    def __init__(self, base_url="https://demobackend.emergentagent.com"):
        # Get the correct backend URL from frontend .env
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []

    def log_result(self, test_name, success, details=None, error=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
            if error:
                print(f"   Error: {error}")
        
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        })

    def test_health_check(self):
        """Test 1: Health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check expected health response structure
                expected_fields = ["status", "timestamp", "directories"]
                has_all_fields = all(field in data for field in expected_fields)
                
                if has_all_fields and data.get("status") == "healthy":
                    self.log_result("Health Check", True, {
                        "status": data.get("status"),
                        "directories": data.get("directories", {}),
                        "timestamp": data.get("timestamp")
                    })
                    return True
                else:
                    self.log_result("Health Check", False, data, "Missing expected fields or unhealthy status")
                    return False
            else:
                self.log_result("Health Check", False, None, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Health Check", False, None, str(e))
            return False

    def test_get_posts(self):
        """Test 2: Get posts endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/posts", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check expected response structure
                if "posts" in data and isinstance(data["posts"], list):
                    self.log_result("Get Posts", True, {
                        "posts_count": len(data["posts"]),
                        "total": data.get("total", 0)
                    })
                    return True
                else:
                    self.log_result("Get Posts", False, data, "Invalid response structure")
                    return False
            else:
                self.log_result("Get Posts", False, None, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Get Posts", False, None, str(e))
            return False

    def test_create_post(self):
        """Test 3: Create post endpoint"""
        try:
            post_data = {
                "content": "Test post from backend test suite",
                "media_urls": ["https://picsum.photos/800/600"],
                "platform": "facebook"
            }
            
            response = requests.post(
                f"{self.base_url}/api/posts", 
                json=post_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check expected response structure
                expected_fields = ["id", "content", "media_urls", "platform", "status", "created_at"]
                has_all_fields = all(field in data for field in expected_fields)
                
                if has_all_fields:
                    self.log_result("Create Post", True, {
                        "post_id": data.get("id"),
                        "platform": data.get("platform"),
                        "status": data.get("status"),
                        "media_count": len(data.get("media_urls", []))
                    })
                    return True, data.get("id")
                else:
                    self.log_result("Create Post", False, data, "Missing expected fields in response")
                    return False, None
            else:
                self.log_result("Create Post", False, None, f"HTTP {response.status_code}: {response.text}")
                return False, None
                
        except Exception as e:
            self.log_result("Create Post", False, None, str(e))
            return False, None

    def test_upload_file(self):
        """Test 4: File upload endpoint"""
        try:
            # Create a simple test image content
            test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
            
            files = {
                'file': ('test_image.png', test_image_content, 'image/png')
            }
            
            response = requests.post(
                f"{self.base_url}/api/upload",
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check expected response structure
                expected_fields = ["url", "filename"]
                has_required_fields = all(field in data for field in expected_fields)
                
                if has_required_fields:
                    self.log_result("File Upload", True, {
                        "url": data.get("url"),
                        "filename": data.get("filename"),
                        "processed": data.get("processed", False)
                    })
                    return True
                else:
                    self.log_result("File Upload", False, data, "Missing expected fields in response")
                    return False
            else:
                self.log_result("File Upload", False, None, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("File Upload", False, None, str(e))
            return False

    def test_webhook_endpoint(self):
        """Test 5: Webhook endpoint"""
        try:
            # Test webhook with simple data
            webhook_data = {
                "event": "test",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {"test": "webhook_test"}
            }
            
            response = requests.post(
                f"{self.base_url}/api/webhook",
                json=webhook_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check expected response structure
                if "status" in data and "timestamp" in data:
                    self.log_result("Webhook", True, {
                        "status": data.get("status"),
                        "timestamp": data.get("timestamp")
                    })
                    return True
                else:
                    self.log_result("Webhook", False, data, "Invalid response structure")
                    return False
            else:
                self.log_result("Webhook", False, None, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Webhook", False, None, str(e))
            return False

    def test_invalid_platform_validation(self):
        """Test 6: Platform validation in post creation"""
        try:
            post_data = {
                "content": "Test post with invalid platform",
                "platform": "invalid_platform"  # Should fail validation
            }
            
            response = requests.post(
                f"{self.base_url}/api/posts", 
                json=post_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            # Should return 422 for validation error
            if response.status_code == 422:
                self.log_result("Platform Validation", True, {
                    "validation_error": "Correctly rejected invalid platform"
                })
                return True
            else:
                self.log_result("Platform Validation", False, None, 
                              f"Expected 422 validation error, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Platform Validation", False, None, str(e))
            return False

    def run_all_tests(self):
        """Execute all tests"""
        print("🧪 STARTING META PUBLISHING PLATFORM BACKEND TESTS")
        print("=" * 60)
        print(f"Testing backend at: {self.base_url}")
        print()
        
        # Test 1: Health Check (critical)
        if not self.test_health_check():
            print("❌ Backend health check failed - Stopping tests")
            return False
        
        # Test 2: Get Posts
        self.test_get_posts()
        
        # Test 3: Create Post
        post_created, post_id = self.test_create_post()
        
        # Test 4: File Upload
        self.test_upload_file()
        
        # Test 5: Webhook
        self.test_webhook_endpoint()
        
        # Test 6: Platform Validation
        self.test_invalid_platform_validation()
        
        # Final Summary
        print("\n" + "=" * 60)
        print("📊 BACKEND TEST RESULTS SUMMARY")
        print("=" * 60)
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        
        print(f"Tests executed: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if success_rate >= 85:
            print("✅ BACKEND STATUS: FULLY FUNCTIONAL")
            print("🎯 All critical endpoints working correctly")
        elif success_rate >= 70:
            print("⚠️ BACKEND STATUS: MOSTLY FUNCTIONAL")
            print("🔧 Minor issues detected, but core functionality works")
        else:
            print("❌ BACKEND STATUS: MAJOR ISSUES DETECTED")
            print("🚨 Significant problems need to be addressed")
        
        # List failed tests
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test.get('error', 'Unknown error')}")
        
        print("\n🔍 DETAILED RESULTS:")
        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}")
            if result.get("details"):
                print(f"      Details: {result['details']}")
        
        return success_rate >= 70

def main():
    """Main entry point"""
    print("🚀 Meta Publishing Platform Backend Test Suite")
    print("Testing compilation fixes and endpoint functionality")
    print()
    
    tester = MetaPublishingTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())