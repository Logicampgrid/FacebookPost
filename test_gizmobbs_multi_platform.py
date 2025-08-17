#!/usr/bin/env python3
"""
Test script for gizmobbs multi-platform publication and video support
"""

import requests
import json
import os
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8001"

def test_gizmobbs_multi_platform():
    """Test that gizmobbs store publishes to both Facebook and Instagram"""
    print("🧪 Testing gizmobbs multi-platform publication...")
    
    try:
        # Test endpoint to verify outdoor shop mapping
        response = requests.get(f"{API_BASE}/api/debug/store-platforms/gizmobbs")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Store platforms response: {data}")
            
            total_platforms = data.get('total_platforms', 0)
            platforms = data.get('platforms', {})
            
            print(f"📊 Total platforms for gizmobbs: {total_platforms}")
            print(f"📘 Main Facebook page: {platforms.get('main_page', {}).get('name', 'N/A')}")
            print(f"📸 Instagram accounts: {len(platforms.get('instagram_accounts', []))}")
            
            # Check if we have both platforms
            has_facebook = bool(platforms.get('main_page'))
            has_instagram = len(platforms.get('instagram_accounts', [])) > 0
            
            if has_facebook and has_instagram:
                print("✅ PERFECT: gizmobbs has access to both Facebook and Instagram!")
                return True
            else:
                print(f"⚠️ WARNING: gizmobbs missing platforms - Facebook: {has_facebook}, Instagram: {has_instagram}")
                return False
                
        else:
            print(f"❌ Error getting store platforms: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"💥 Test error: {e}")
        return False

def test_video_webhook():
    """Test video upload via webhook"""
    print("\n🎬 Testing video upload via webhook...")
    
    try:
        # Test webhook info endpoint
        response = requests.get(f"{API_BASE}/api/webhook")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Webhook info received")
            
            # Check if video types are mentioned
            required_fields = data.get('required_fields', {})
            image_field = required_fields.get('image', '')
            
            if 'MP4' in image_field or 'video' in image_field.lower():
                print("✅ Video support confirmed in webhook documentation")
                return True
            else:
                print(f"⚠️ Video support not clearly documented: {image_field}")
                return False
                
        else:
            print(f"❌ Error getting webhook info: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Test error: {e}")
        return False

def test_health_check():
    """Test backend health"""
    print("\n❤️ Testing backend health...")
    
    try:
        response = requests.get(f"{API_BASE}/api/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend health: {data.get('status', 'unknown')}")
            print(f"📊 MongoDB: {data.get('mongodb', 'unknown')}")
            
            if data.get('database'):
                db_info = data['database']
                print(f"👥 Users: {db_info.get('users_count', 0)}")
                print(f"📝 Posts: {db_info.get('posts_count', 0)}")
            
            return data.get('status') == 'healthy'
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Health check error: {e}")
        return False

def test_shop_mapping_config():
    """Test the shop mapping configuration"""
    print("\n🏪 Testing shop mapping configuration...")
    
    try:
        response = requests.get(f"{API_BASE}/api/webhook")
        
        if response.status_code == 200:
            data = response.json()
            shop_mapping = data.get('shop_mapping', {})
            
            # Check gizmobbs configuration
            gizmobbs_config = shop_mapping.get('gizmobbs', {})
            gimobbs_config = shop_mapping.get('gimobbs', {})
            
            print(f"🐕 gizmobbs config: {gizmobbs_config}")
            print(f"🐕 gimobbs config: {gimobbs_config}")
            
            # Check for multi-platform support
            gizmobbs_platform = gizmobbs_config.get('platform')
            gimobbs_platform = gimobbs_config.get('platform')
            
            if gizmobbs_platform == 'multi' and gimobbs_platform == 'multi':
                print("✅ EXCELLENT: Both gizmobbs and gimobbs configured for multi-platform!")
                
                # Check platforms array
                gizmobbs_platforms = gizmobbs_config.get('platforms', [])
                if 'facebook' in gizmobbs_platforms and 'instagram' in gizmobbs_platforms:
                    print("✅ PERFECT: gizmobbs supports both Facebook and Instagram!")
                    return True
                else:
                    print(f"⚠️ gizmobbs platforms incomplete: {gizmobbs_platforms}")
                    return False
            else:
                print(f"❌ gizmobbs not configured for multi-platform: {gizmobbs_platform}")
                return False
                
        else:
            print(f"❌ Error getting webhook info: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting gizmobbs multi-platform and video support tests\n")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Backend Health
    result = test_health_check()
    test_results.append(("Backend Health", result))
    
    # Test 2: Shop Configuration
    result = test_shop_mapping_config()
    test_results.append(("Shop Multi-Platform Config", result))
    
    # Test 3: Platform Access
    result = test_gizmobbs_multi_platform()
    test_results.append(("Platform Access", result))
    
    # Test 4: Video Support
    result = test_video_webhook()
    test_results.append(("Video Support", result))
    
    # Results Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! gizmobbs multi-platform + video support is ready!")
    else:
        print("⚠️ Some tests failed. Check the details above.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    main()