import requests
import sys
import json
import io
import os
from datetime import datetime
import uuid

class VideoMultiPlatformTester:
    def __init__(self, base_url="https://ok-simple-20.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        
        # Don't set Content-Type for multipart requests
        if not files:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files)
                else:
                    response = requests.post(url, json=data, headers=headers)

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

    def test_webhook_info_video_support(self):
        """Test webhook info endpoint shows video support"""
        success, response = self.run_test(
            "Webhook Info - Video Support",
            "GET",
            "api/webhook",
            200
        )
        
        if success:
            required_fields = response.get("required_fields", {})
            image_field = required_fields.get("image", "")
            features = response.get("features", [])
            
            # Check if video formats are mentioned
            video_formats = ["MP4", "MOV", "AVI", "WebM"]
            video_support_found = False
            
            for format in video_formats:
                if format in image_field:
                    video_support_found = True
                    print(f"✅ Video format {format} supported in image field")
            
            if not video_support_found:
                print("❌ No video formats found in image field description")
                return False
            
            # Check features list for video support
            video_feature_found = any("video" in feature.lower() for feature in features)
            if video_feature_found:
                print("✅ Video support mentioned in features")
            else:
                print("⚠️ Video support not explicitly mentioned in features")
            
            return True
        
        return success

    def test_webhook_gizmobbs_multi_platform(self):
        """Test webhook info shows gizmobbs multi-platform support"""
        success, response = self.run_test(
            "Webhook Info - Gizmobbs Multi-Platform",
            "GET",
            "api/webhook",
            200
        )
        
        if success:
            shop_mapping = response.get("shop_mapping", {})
            gizmobbs_config = shop_mapping.get("gizmobbs", {})
            
            print(f"   Gizmobbs config: {gizmobbs_config}")
            
            # Check if gizmobbs has multi-platform configuration
            platform = gizmobbs_config.get("platform")
            platforms = gizmobbs_config.get("platforms", [])
            
            if platform == "multi":
                print("✅ Gizmobbs configured for multi-platform")
            else:
                print(f"❌ Gizmobbs platform should be 'multi', got: {platform}")
                return False
            
            if "facebook" in platforms and "instagram" in platforms:
                print("✅ Gizmobbs supports both Facebook and Instagram")
            else:
                print(f"❌ Gizmobbs platforms should include Facebook and Instagram, got: {platforms}")
                return False
            
            # Check Instagram username
            instagram_username = gizmobbs_config.get("instagram_username")
            if instagram_username == "logicamp_berger":
                print("✅ Correct Instagram username configured")
            else:
                print(f"❌ Expected Instagram username 'logicamp_berger', got: {instagram_username}")
                return False
            
            return True
        
        return success

    def create_test_video_file(self, filename="test_video.mp4", size_kb=50):
        """Create a small test video file for upload testing"""
        # Create a minimal MP4-like file (not a real video, but has correct extension)
        content = b"fake_mp4_content_for_testing" * (size_kb * 1024 // 30)
        return io.BytesIO(content)

    def create_test_image_file(self, filename="test_image.jpg", size_kb=20):
        """Create a small test image file for comparison"""
        content = b"fake_jpg_content_for_testing" * (size_kb * 1024 // 30)
        return io.BytesIO(content)

    def test_webhook_video_upload_mp4(self):
        """Test webhook with MP4 video upload"""
        # Create test video file
        video_file = self.create_test_video_file("test_video.mp4")
        
        # JSON data for the webhook
        json_data = {
            "title": "Test Video Product",
            "description": "This is a test video upload to verify MP4 support",
            "url": "https://example.com/test-video-product",
            "store": "gizmobbs"
        }
        
        files = {
            'image': ('test_video.mp4', video_file, 'video/mp4')
        }
        
        data = {
            'json_data': json.dumps(json_data)
        }
        
        success, response = self.run_test(
            "Webhook Video Upload - MP4",
            "POST",
            "api/webhook",
            200,
            data=data,
            files=files
        )
        
        if success:
            status = response.get("status")
            data_response = response.get("data", {})
            image_filename = data_response.get("image_filename", "")
            publication_results = data_response.get("publication_results", [])
            
            if status == "success":
                print("✅ Video upload successful")
            else:
                print(f"❌ Upload failed with status: {status}")
                return False
            
            # Check if filename indicates video
            if image_filename.endswith('.mp4'):
                print("✅ Video file saved with correct extension")
            else:
                print(f"⚠️ Expected .mp4 extension, got: {image_filename}")
            
            # Check publication results for gizmobbs multi-platform
            if publication_results:
                pub_result = publication_results[0]
                platforms = pub_result.get("platforms", [])
                print(f"   Publication platforms: {len(platforms)} platforms")
                
                # Should publish to both Facebook and Instagram for gizmobbs
                facebook_found = any("facebook" in str(p).lower() for p in platforms)
                instagram_found = any("instagram" in str(p).lower() for p in platforms)
                
                if facebook_found and instagram_found:
                    print("✅ Multi-platform publishing attempted (Facebook + Instagram)")
                elif facebook_found:
                    print("⚠️ Only Facebook publishing found")
                elif instagram_found:
                    print("⚠️ Only Instagram publishing found")
                else:
                    print("❌ No platform publishing detected")
            
            return True
        
        return success

    def test_webhook_video_upload_mov(self):
        """Test webhook with MOV video upload"""
        # Create test MOV file
        video_file = self.create_test_video_file("test_video.mov")
        
        json_data = {
            "title": "Test MOV Video Product",
            "description": "Testing MOV video format support",
            "url": "https://example.com/test-mov-product",
            "store": "outdoor"
        }
        
        files = {
            'image': ('test_video.mov', video_file, 'video/quicktime')
        }
        
        data = {
            'json_data': json.dumps(json_data)
        }
        
        success, response = self.run_test(
            "Webhook Video Upload - MOV",
            "POST",
            "api/webhook",
            200,
            data=data,
            files=files
        )
        
        if success:
            data_response = response.get("data", {})
            image_filename = data_response.get("image_filename", "")
            
            if image_filename.endswith('.mov'):
                print("✅ MOV video file saved with correct extension")
            else:
                print(f"⚠️ Expected .mov extension, got: {image_filename}")
            
            return True
        
        return success

    def test_webhook_video_upload_webm(self):
        """Test webhook with WebM video upload"""
        video_file = self.create_test_video_file("test_video.webm")
        
        json_data = {
            "title": "Test WebM Video Product",
            "description": "Testing WebM video format support",
            "url": "https://example.com/test-webm-product"
        }
        
        files = {
            'image': ('test_video.webm', video_file, 'video/webm')
        }
        
        data = {
            'json_data': json.dumps(json_data)
        }
        
        success, response = self.run_test(
            "Webhook Video Upload - WebM",
            "POST",
            "api/webhook",
            200,
            data=data,
            files=files
        )
        
        if success:
            data_response = response.get("data", {})
            image_filename = data_response.get("image_filename", "")
            
            if image_filename.endswith('.webm'):
                print("✅ WebM video file saved with correct extension")
            else:
                print(f"⚠️ Expected .webm extension, got: {image_filename}")
            
            return True
        
        return success

    def test_webhook_invalid_video_format(self):
        """Test webhook rejects invalid video formats"""
        video_file = self.create_test_video_file("test_video.avi")
        
        json_data = {
            "title": "Test Invalid Video",
            "description": "Testing invalid video format rejection",
            "url": "https://example.com/test-invalid"
        }
        
        files = {
            'image': ('test_video.avi', video_file, 'video/x-msvideo')  # AVI should be supported
        }
        
        data = {
            'json_data': json.dumps(json_data)
        }
        
        success, response = self.run_test(
            "Webhook Video Upload - AVI (should be supported)",
            "POST",
            "api/webhook",
            200,  # AVI should actually be supported based on the code
            data=data,
            files=files
        )
        
        return success

    def test_webhook_unsupported_format(self):
        """Test webhook rejects truly unsupported formats"""
        fake_file = io.BytesIO(b"fake_content")
        
        json_data = {
            "title": "Test Unsupported Format",
            "description": "Testing unsupported format rejection",
            "url": "https://example.com/test-unsupported"
        }
        
        files = {
            'image': ('test_file.txt', fake_file, 'text/plain')
        }
        
        data = {
            'json_data': json.dumps(json_data)
        }
        
        success, response = self.run_test(
            "Webhook Upload - Unsupported Format (should fail)",
            "POST",
            "api/webhook",
            400,  # Should reject unsupported formats
            data=data,
            files=files
        )
        
        if success:
            detail = response.get("detail", "")
            if "invalid media type" in detail.lower() or "allowed" in detail.lower():
                print("✅ Correctly rejected unsupported format")
            else:
                print(f"⚠️ Unexpected error message: {detail}")
        
        return success

    def test_gizmobbs_multi_platform_config(self):
        """Test that gizmobbs store configuration shows multi-platform"""
        success, response = self.run_test(
            "Gizmobbs Multi-Platform Configuration",
            "GET",
            "api/debug/store-platforms/gizmobbs",
            200
        )
        
        if success:
            shop_type = response.get("shop_type")
            platforms = response.get("platforms", {})
            shop_mapping_config = response.get("shop_mapping_config", {})
            
            print(f"   Shop type: {shop_type}")
            print(f"   Platforms found: {platforms}")
            
            # Check shop mapping configuration
            platform_config = shop_mapping_config.get("platform")
            platforms_list = shop_mapping_config.get("platforms", [])
            instagram_username = shop_mapping_config.get("instagram_username")
            
            if platform_config == "multi":
                print("✅ Gizmobbs configured as multi-platform")
            else:
                print(f"❌ Expected platform 'multi', got: {platform_config}")
                return False
            
            if "facebook" in platforms_list and "instagram" in platforms_list:
                print("✅ Both Facebook and Instagram platforms configured")
            else:
                print(f"❌ Expected Facebook and Instagram, got: {platforms_list}")
                return False
            
            if instagram_username == "logicamp_berger":
                print("✅ Correct Instagram username configured")
            else:
                print(f"❌ Expected 'logicamp_berger', got: {instagram_username}")
                return False
            
            return True
        
        return success

    def test_outdoor_single_platform_config(self):
        """Test that outdoor store remains single platform (Facebook only)"""
        success, response = self.run_test(
            "Outdoor Single Platform Configuration",
            "GET",
            "api/debug/store-platforms/outdoor",
            200
        )
        
        if success:
            shop_mapping_config = response.get("shop_mapping_config", {})
            platform_config = shop_mapping_config.get("platform")
            
            if platform_config == "facebook":
                print("✅ Outdoor correctly configured as Facebook-only")
            else:
                print(f"⚠️ Outdoor platform config: {platform_config}")
            
            return True
        
        return success

    def test_video_optimization_endpoint(self):
        """Test if there's a video optimization endpoint or feature"""
        # This might not exist, but let's check
        success, response = self.run_test(
            "Video Optimization Info",
            "GET",
            "api/debug/video-optimization",
            200  # Might return 404 if not implemented
        )
        
        # This test is exploratory - it's OK if it fails
        if not success:
            print("ℹ️  Video optimization endpoint not found (this is OK)")
            return True
        
        return success

    def test_webhook_large_video_handling(self):
        """Test webhook with larger video file"""
        # Create a larger test file (simulate 5MB)
        large_video = self.create_test_video_file("large_video.mp4", size_kb=5000)
        
        json_data = {
            "title": "Large Video Test",
            "description": "Testing large video file handling",
            "url": "https://example.com/large-video",
            "store": "gizmobbs"
        }
        
        files = {
            'image': ('large_video.mp4', large_video, 'video/mp4')
        }
        
        data = {
            'json_data': json.dumps(json_data)
        }
        
        success, response = self.run_test(
            "Webhook Large Video Upload",
            "POST",
            "api/webhook",
            200,
            data=data,
            files=files
        )
        
        if success:
            data_response = response.get("data", {})
            image_size_bytes = data_response.get("image_size_bytes", 0)
            
            print(f"   Uploaded file size: {image_size_bytes} bytes ({image_size_bytes/1024/1024:.1f} MB)")
            
            if image_size_bytes > 1000000:  # > 1MB
                print("✅ Large video file handled successfully")
            else:
                print("⚠️ File size smaller than expected")
            
            return True
        
        return success

    def test_webhook_json_validation(self):
        """Test webhook JSON validation with video"""
        video_file = self.create_test_video_file("test.mp4")
        
        # Test with missing required fields
        invalid_json_data = {
            "title": "Test Video",
            # Missing description and url
            "store": "gizmobbs"
        }
        
        files = {
            'image': ('test.mp4', video_file, 'video/mp4')
        }
        
        data = {
            'json_data': json.dumps(invalid_json_data)
        }
        
        success, response = self.run_test(
            "Webhook JSON Validation (Invalid)",
            "POST",
            "api/webhook",
            400,  # Should fail validation
            data=data,
            files=files
        )
        
        if success:
            detail = response.get("detail", "")
            if "validation" in detail.lower() or "required" in detail.lower():
                print("✅ JSON validation working correctly")
            else:
                print(f"⚠️ Unexpected validation error: {detail}")
        
        return success

    def run_all_tests(self):
        """Run all video and multi-platform tests"""
        print("🚀 Starting Video & Multi-Platform Tests")
        print("=" * 60)
        
        tests = [
            self.test_webhook_info_video_support,
            self.test_webhook_gizmobbs_multi_platform,
            self.test_webhook_video_upload_mp4,
            self.test_webhook_video_upload_mov,
            self.test_webhook_video_upload_webm,
            self.test_webhook_invalid_video_format,
            self.test_webhook_unsupported_format,
            self.test_gizmobbs_multi_platform_config,
            self.test_outdoor_single_platform_config,
            self.test_video_optimization_endpoint,
            self.test_webhook_large_video_handling,
            self.test_webhook_json_validation,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
                self.tests_run += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Video & Multi-Platform Tests Summary")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = VideoMultiPlatformTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())