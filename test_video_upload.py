#!/usr/bin/env python3
"""
Test video upload functionality
"""

import requests
import io
import json

API_BASE = "http://localhost:8001"

def create_test_video_data():
    """Create a simple test 'video' (actually just test data)"""
    # Create some dummy video-like data
    video_data = b"FAKE_VIDEO_DATA_FOR_TESTING" * 100
    return video_data

def test_webhook_video_upload():
    """Test video upload via multipart webhook"""
    print("🎬 Testing video upload via webhook...")
    
    try:
        # Create test video data
        video_data = create_test_video_data()
        
        # Prepare test data
        json_data = {
            "title": "Test Video Product",
            "description": "This is a test video for gizmobbs multi-platform publication",
            "url": "https://gizmobbs.com/test-product-video",
            "store": "gizmobbs"
        }
        
        # Prepare multipart request
        files = {
            'image': ('test_video.mp4', io.BytesIO(video_data), 'video/mp4')
        }
        
        data = {
            'json_data': json.dumps(json_data)
        }
        
        print(f"📤 Sending test video to webhook...")
        print(f"📄 JSON data: {json_data}")
        print(f"🎥 Video size: {len(video_data)} bytes")
        
        response = requests.post(f"{API_BASE}/api/webhook", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook video upload successful!")
            print(f"📁 Saved as: {result['data']['image_filename']}")
            print(f"🔗 URL: {result['data']['image_url']}")
            
            # Check publication results
            pub_results = result['data'].get('publication_results', [])
            if pub_results:
                for pub_result in pub_results:
                    print(f"📢 Publication: {pub_result['status']} - {pub_result['message']}")
                    
            return True
        else:
            print(f"❌ Webhook upload failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"💥 Video upload test error: {e}")
        return False

def test_facebook_image_debug():
    """Test Facebook image display debug endpoint"""
    print("\n🔍 Testing Facebook image display debug...")
    
    try:
        response = requests.get(f"{API_BASE}/api/debug/facebook-image-fix")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Facebook image debug successful")
            print(f"🎯 Status: {data.get('status')}")
            print(f"📸 Image guarantee: {data.get('image_display_guarantee')}")
            
            strategies = data.get('strategies_available', [])
            for strategy in strategies:
                print(f"  • {strategy}")
                
            return True
        else:
            print(f"❌ Debug failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Debug test error: {e}")
        return False

def main():
    """Run video tests"""
    print("🎬 Starting video support tests\n")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Facebook Debug
    result = test_facebook_image_debug()
    test_results.append(("Facebook Debug", result))
    
    # Test 2: Video Upload
    result = test_webhook_video_upload()
    test_results.append(("Video Webhook Upload", result))
    
    # Results
    print("\n" + "=" * 50)
    print("📊 VIDEO TESTS SUMMARY")
    print("=" * 50)
    
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("=" * 50)

if __name__ == "__main__":
    main()