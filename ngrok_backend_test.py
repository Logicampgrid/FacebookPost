#!/usr/bin/env python3
"""
Backend API Test Suite for FacebookPost Application
Testing the ngrok deployment: https://21da467d7e90.ngrok-free.app
"""

import requests
import sys
import json
from datetime import datetime
import time

class FacebookPostAPITester:
    def __init__(self, base_url="https://21da467d7e90.ngrok-free.app"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.session = requests.Session()
        # Add headers to avoid ngrok browser warning
        self.session.headers.update({
            'User-Agent': 'FacebookPost-TestAgent/1.0',
            'ngrok-skip-browser-warning': 'true'
        })

    def log(self, message, level="INFO"):
        """Log test messages with timestamp"""
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
        icon = icons.get(level.upper(), "📋")
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{icon} [{timestamp}] {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        test_headers = self.session.headers.copy()
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        self.log(f"Testing {name}...", "TEST")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}", "SUCCESS")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        self.log(f"   Response: {response_data}", "INFO")
                except:
                    self.log(f"   Response: {response.text[:200]}...", "INFO")
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}", "ERROR")
                self.log(f"   Response: {response.text[:300]}...", "ERROR")

            return success, response

        except requests.exceptions.Timeout:
            self.log(f"❌ {name} - Timeout after 30 seconds", "ERROR")
            return False, None
        except requests.exceptions.ConnectionError:
            self.log(f"❌ {name} - Connection error", "ERROR")
            return False, None
        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}", "ERROR")
            return False, None

    def test_health_check(self):
        """Test the health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "/api/health",
            200
        )
        
        if success and response:
            try:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log("   Health status: HEALTHY", "SUCCESS")
                    return True
                else:
                    self.log(f"   Unexpected health status: {data.get('status')}", "WARNING")
            except:
                pass
        return success

    def test_webhook_endpoint(self):
        """Test webhook endpoint"""
        webhook_data = {
            "store": "gizmobbs",
            "message": "Test automatique depuis testing agent",
            "product_url": "https://example.com",
            "image_url": "https://example.com/test-image.jpg"
        }
        
        success, response = self.run_test(
            "Webhook POST",
            "POST",
            "/api/webhook",
            200,
            data=webhook_data
        )
        return success

    def test_publish_endpoint_image(self):
        """Test publish endpoint with image (should use Facebook/feed API)"""
        publish_data = {
            "store": "gizmobbs",
            "message": "Test automatique depuis testing agent - IMAGE",
            "product_url": "https://example.com",
            "image_url": "https://picsum.photos/800/600",
            "platforms": ["facebook"]
        }
        
        success, response = self.run_test(
            "Publish with Image (Facebook/feed API)",
            "POST",
            "/api/publish",
            200,
            data=publish_data
        )
        
        if success and response:
            try:
                data = response.json()
                self.log(f"   Image publish result: {data.get('success', 'Unknown')}", "INFO")
                if data.get('facebook_result'):
                    self.log("   ✅ Facebook feed API used for image", "SUCCESS")
            except:
                pass
        
        return success

    def test_publish_endpoint_video(self):
        """Test publish endpoint with video (should use Facebook/videos API)"""
        publish_data = {
            "store": "gizmobbs",
            "message": "Test automatique depuis testing agent - VIDEO",
            "product_url": "https://example.com",
            "video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4",
            "platforms": ["facebook"]
        }
        
        success, response = self.run_test(
            "Publish with Video (Facebook/videos API)",
            "POST",
            "/api/publish",
            200,
            data=publish_data
        )
        
        if success and response:
            try:
                data = response.json()
                self.log(f"   Video publish result: {data.get('success', 'Unknown')}", "INFO")
                if data.get('facebook_result'):
                    self.log("   ✅ Facebook videos API used for video", "SUCCESS")
            except:
                pass
        
        return success

    def test_stores_configuration(self):
        """Test stores configuration endpoint"""
        success, response = self.run_test(
            "Stores Configuration",
            "GET",
            "/api/stores",
            200
        )
        
        if success and response:
            try:
                data = response.json()
                stores = data.get('stores', {})
                self.log(f"   Available stores: {list(stores.keys())}", "INFO")
                if 'gizmobbs' in stores:
                    self.log("   ✅ gizmobbs store configured", "SUCCESS")
                else:
                    self.log("   ⚠️ gizmobbs store not found", "WARNING")
            except:
                pass
        
        return success

    def test_pages_info(self):
        """Test pages information endpoint"""
        success, response = self.run_test(
            "Pages Information",
            "GET",
            "/api/pages",
            200
        )
        return success

    def test_video_vs_image_detection(self):
        """Critical test: Verify automatic video vs image detection"""
        self.log("🎯 CRITICAL TEST: Video vs Image Detection", "TEST")
        
        # Test 1: Image URL should trigger Facebook/feed API
        image_data = {
            "store": "gizmobbs",
            "message": "Test détection automatique - IMAGE",
            "product_url": "https://example.com",
            "image_url": "https://picsum.photos/800/600"
        }
        
        success1, response1 = self.run_test(
            "Auto-detection: Image Content",
            "POST",
            "/api/publish",
            200,
            data=image_data
        )
        
        # Test 2: Video URL should trigger Facebook/videos API
        video_data = {
            "store": "gizmobbs", 
            "message": "Test détection automatique - VIDEO",
            "product_url": "https://example.com",
            "video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
        }
        
        success2, response2 = self.run_test(
            "Auto-detection: Video Content",
            "POST",
            "/api/publish",
            200,
            data=video_data
        )
        
        detection_success = success1 and success2
        if detection_success:
            self.log("✅ CRITICAL: Video vs Image detection working", "SUCCESS")
        else:
            self.log("❌ CRITICAL: Video vs Image detection FAILED", "ERROR")
        
        return detection_success

    def run_all_tests(self):
        """Run all backend tests"""
        self.log("🚀 Starting FacebookPost Backend API Tests", "INFO")
        self.log(f"🌐 Testing URL: {self.base_url}", "INFO")
        self.log("=" * 60, "INFO")
        
        # Basic connectivity and health
        self.test_health_check()
        
        # Configuration endpoints
        self.test_stores_configuration()
        self.test_pages_info()
        
        # Webhook functionality
        self.test_webhook_endpoint()
        
        # Publication functionality
        self.test_publish_endpoint_image()
        self.test_publish_endpoint_video()
        
        # Critical functionality
        self.test_video_vs_image_detection()
        
        # Results summary
        self.log("=" * 60, "INFO")
        self.log(f"📊 Tests completed: {self.tests_passed}/{self.tests_run} passed", "INFO")
        
        if self.tests_passed == self.tests_run:
            self.log("🎉 All tests PASSED!", "SUCCESS")
            return 0
        elif self.tests_passed > 0:
            self.log(f"⚠️ Partial success: {self.tests_run - self.tests_passed} tests failed", "WARNING")
            return 1
        else:
            self.log("❌ All tests FAILED!", "ERROR")
            return 2

def main():
    """Main test execution"""
    tester = FacebookPostAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())