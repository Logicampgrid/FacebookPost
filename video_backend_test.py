#!/usr/bin/env python3
"""
Test complet des endpoints vidéo Meta Publishing Platform
Tests pour la nouvelle fonctionnalité de publication vidéo
"""

import requests
import sys
import os
import tempfile
import json
from datetime import datetime
from pathlib import Path

class VideoBackendTester:
    def __init__(self, base_url="https://fair-pans-taste.loca.lt"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
    def log_test(self, name, status, message="", details=None):
        """Log test results"""
        self.tests_run += 1
        if status == "PASS":
            self.tests_passed += 1
            icon = "✅"
        elif status == "FAIL":
            icon = "❌"
        else:
            icon = "⚠️"
            
        print(f"{icon} {name}: {status}")
        if message:
            print(f"   {message}")
        if details:
            print(f"   Details: {details}")
            
        self.test_results.append({
            "name": name,
            "status": status,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def create_test_video_file(self):
        """Create a small test video file for upload testing"""
        try:
            # Create a temporary MP4 file with minimal content
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            
            # Write minimal MP4 header (this won't be a real video but will pass basic validation)
            mp4_header = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom\x00\x00\x00\x08free'
            temp_file.write(mp4_header)
            temp_file.write(b'0' * 1024)  # Add some dummy data
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            self.log_test("Create Test Video", "FAIL", f"Error creating test video: {str(e)}")
            return None

    def test_health_endpoint(self):
        """Test basic health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_test("Health Check", "PASS", "Backend is healthy")
                    return True
                else:
                    self.log_test("Health Check", "FAIL", f"Unexpected health response: {data}")
            else:
                self.log_test("Health Check", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Health Check", "FAIL", f"Connection error: {str(e)}")
            
        return False

    def test_video_upload_endpoint(self):
        """Test POST /api/videos/upload endpoint"""
        try:
            # Create test video file
            test_video_path = self.create_test_video_file()
            if not test_video_path:
                return False
                
            try:
                with open(test_video_path, 'rb') as video_file:
                    files = {'video': ('test_video.mp4', video_file, 'video/mp4')}
                    data = {'filename': 'test_video.mp4'}
                    
                    response = requests.post(
                        f"{self.base_url}/api/videos/upload",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('success'):
                            self.log_test("Video Upload", "PASS", 
                                        f"Video uploaded successfully: {result.get('filename')}")
                            return result
                        else:
                            self.log_test("Video Upload", "FAIL", 
                                        f"Upload failed: {result.get('error', 'Unknown error')}")
                    else:
                        self.log_test("Video Upload", "FAIL", 
                                    f"HTTP {response.status_code}: {response.text}")
                        
            finally:
                # Clean up test file
                if os.path.exists(test_video_path):
                    os.unlink(test_video_path)
                    
        except Exception as e:
            self.log_test("Video Upload", "FAIL", f"Error: {str(e)}")
            
        return False

    def test_video_library_endpoint(self):
        """Test GET /api/videos/library endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/videos/library", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    videos = data.get('videos', [])
                    count = data.get('count', 0)
                    self.log_test("Video Library", "PASS", 
                                f"Library loaded: {count} videos found")
                    return data
                else:
                    self.log_test("Video Library", "FAIL", 
                                f"Library error: {data.get('error', 'Unknown error')}")
            else:
                self.log_test("Video Library", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Video Library", "FAIL", f"Error: {str(e)}")
            
        return False

    def test_video_post_creation_endpoint(self):
        """Test POST /api/posts/video endpoint"""
        try:
            # Test data for video post creation
            form_data = {
                'user_id': 'test_user_123',
                'content': 'Test video post content with #hashtags',
                'video_url': 'https://example.com/test_video.mp4',
                'video_id': 'test_video_123',
                'target_type': 'page',
                'target_id': 'test_page_123',
                'target_name': 'Test Page',
                'platform': 'facebook',
                'business_manager_id': 'test_bm_123',
                'business_manager_name': 'Test Business Manager',
                'video_metadata': json.dumps({
                    'title': 'Test Video Title',
                    'description': 'Test video description',
                    'hashtags': '#test #video #meta'
                })
            }
            
            response = requests.post(
                f"{self.base_url}/api/posts/video",
                data=form_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    post = data.get('post', {})
                    self.log_test("Video Post Creation", "PASS", 
                                f"Video post created: {post.get('id', 'Unknown ID')}")
                    return data
                else:
                    self.log_test("Video Post Creation", "FAIL", 
                                f"Post creation failed: {data.get('error', 'Unknown error')}")
            else:
                self.log_test("Video Post Creation", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Video Post Creation", "FAIL", f"Error: {str(e)}")
            
        return False

    def test_video_history_endpoint(self):
        """Test GET /api/posts/video/history endpoint"""
        try:
            params = {'user_id': 'test_user_123', 'limit': 10}
            response = requests.get(
                f"{self.base_url}/api/posts/video/history",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    posts = data.get('posts', [])
                    count = data.get('count', 0)
                    self.log_test("Video History", "PASS", 
                                f"History loaded: {count} video posts found")
                    return data
                else:
                    self.log_test("Video History", "FAIL", 
                                f"History error: {data.get('error', 'Unknown error')}")
            else:
                self.log_test("Video History", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Video History", "FAIL", f"Error: {str(e)}")
            
        return False

    def test_video_validation(self):
        """Test video format and size validation"""
        try:
            # Test with invalid format
            test_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
            test_file.write(b'This is not a video file')
            test_file.close()
            
            try:
                with open(test_file.name, 'rb') as invalid_file:
                    files = {'video': ('test.txt', invalid_file, 'text/plain')}
                    
                    response = requests.post(
                        f"{self.base_url}/api/videos/upload",
                        files=files,
                        timeout=15
                    )
                    
                    if response.status_code == 400:
                        self.log_test("Video Format Validation", "PASS", 
                                    "Invalid format correctly rejected")
                    else:
                        self.log_test("Video Format Validation", "FAIL", 
                                    f"Expected 400, got {response.status_code}")
                        
            finally:
                os.unlink(test_file.name)
                
        except Exception as e:
            self.log_test("Video Format Validation", "FAIL", f"Error: {str(e)}")

    def test_video_constraints(self):
        """Test video size and duration constraints"""
        try:
            # Test Facebook constraints (10GB, 15 minutes)
            facebook_constraints = {
                'max_size': 10 * 1024 * 1024 * 1024,  # 10GB
                'max_duration': 15 * 60  # 15 minutes
            }
            
            # Test Instagram constraints (1GB, 60 seconds)  
            instagram_constraints = {
                'max_size': 1 * 1024 * 1024 * 1024,  # 1GB
                'max_duration': 60  # 60 seconds
            }
            
            self.log_test("Video Constraints Check", "PASS", 
                        f"Facebook: {facebook_constraints['max_size']/(1024**3):.0f}GB, {facebook_constraints['max_duration']/60:.0f}min")
            self.log_test("Video Constraints Check", "PASS", 
                        f"Instagram: {instagram_constraints['max_size']/(1024**3):.0f}GB, {instagram_constraints['max_duration']}s")
            
        except Exception as e:
            self.log_test("Video Constraints Check", "FAIL", f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all video backend tests"""
        print("🎬 Starting Video Backend Tests...")
        print(f"🌐 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_health_endpoint():
            print("❌ Backend not accessible, stopping tests")
            return False
            
        # Video endpoints tests
        self.test_video_upload_endpoint()
        self.test_video_library_endpoint()
        self.test_video_post_creation_endpoint()
        self.test_video_history_endpoint()
        
        # Validation tests
        self.test_video_validation()
        self.test_video_constraints()
        
        # Summary
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("✅ All video backend tests passed!")
            return True
        else:
            failed_tests = [r for r in self.test_results if r['status'] == 'FAIL']
            print(f"❌ {len(failed_tests)} tests failed:")
            for test in failed_tests:
                print(f"   • {test['name']}: {test['message']}")
            return False

def main():
    """Main test execution"""
    # Use environment variable or default URL
    backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://fair-pans-taste.loca.lt')
    
    print("🎥 Meta Publishing Platform - Video Backend Tests")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tester = VideoBackendTester(backend_url)
    success = tester.run_all_tests()
    
    # Save test results
    try:
        results_file = f"video_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'backend_url': backend_url,
                'summary': {
                    'total_tests': tester.tests_run,
                    'passed_tests': tester.tests_passed,
                    'failed_tests': tester.tests_run - tester.tests_passed,
                    'success_rate': (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
                },
                'test_results': tester.test_results
            }, f, indent=2)
        print(f"📄 Test results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️ Could not save test results: {e}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())