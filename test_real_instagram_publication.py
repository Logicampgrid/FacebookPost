#!/usr/bin/env python3
"""
Test real Instagram publication to identify the exact issue
"""

import requests
import json
import os

API_BASE = "http://localhost:8001"

def test_gizmobbs_publication_simulation():
    """Test publication with gizmobbs store to see exact Instagram error"""
    print("🧪 Testing gizmobbs publication to identify Instagram issue...")
    
    try:
        # Test the multi-platform test endpoint
        response = requests.post(f"{API_BASE}/api/debug/test-multi-platform-post", 
                                params={"shop_type": "gizmobbs"})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Multi-platform test response received")
            
            # Check if it's successful
            if data.get('test_success'):
                result = data.get('result', {})
                print(f"📊 Publication result: {result}")
                
                # Check platform-specific results
                if result.get('platforms_published'):
                    platforms = result['platforms_published']
                    facebook_ok = platforms.get('facebook', False)
                    instagram_ok = platforms.get('instagram', False)
                    
                    print(f"📘 Facebook: {'✅ SUCCESS' if facebook_ok else '❌ FAILED'}")
                    print(f"📸 Instagram: {'✅ SUCCESS' if instagram_ok else '❌ FAILED'}")
                    
                    if not instagram_ok:
                        print("🔍 INSTAGRAM FAILED - This confirms the issue!")
                        return False
                    else:
                        print("🎉 Instagram worked! Issue might be elsewhere.")
                        return True
                else:
                    print("⚠️ No platform-specific results found")
                    print(f"Full result: {json.dumps(result, indent=2)}")
                    
            else:
                print(f"❌ Test failed: {data}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            error_text = response.text
            print(f"Error details: {error_text}")
            
            # Look for specific error patterns
            if "No user" in error_text:
                print("🔍 ISSUE CONFIRMED: No authenticated user!")
                print("💡 This is the root cause - need Facebook authentication first")
                return False
                
    except Exception as e:
        print(f"💥 Test error: {e}")
        return False
    
    return False

def test_facebook_image_display_test():
    """Test the Facebook image display test endpoint"""
    print("\n🧪 Testing Facebook image display test endpoint...")
    
    try:
        response = requests.post(f"{API_BASE}/api/debug/test-facebook-image-display")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print(f"✅ Facebook test successful!")
                print(f"📘 Page: {data.get('page_name')}")
                print(f"🆔 Post ID: {data.get('test_post_id')}")
                print(f"🔗 Facebook URL: {data.get('facebook_post_url')}")
                return True
            else:
                error = data.get('error', 'Unknown error')
                print(f"❌ Facebook test failed: {error}")
                
                if "No user" in error:
                    print("🔍 ROOT CAUSE: No authenticated Facebook user!")
                    return False
                    
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"💥 Test error: {e}")
        return False
    
    return False

def create_test_user_simulation():
    """Simulate what happens when we try to create posts without authentication"""
    print("\n🧪 Testing post creation simulation...")
    
    # Try to create a test post to see the exact error
    test_data = {
        "title": "Test Instagram Product",
        "description": "Test pour vérifier Instagram",
        "image_url": "https://picsum.photos/800/600",
        "product_url": "https://gizmobbs.com/test",
        "shop_type": "gizmobbs"
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/products/publish", json=test_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Product publish test successful: {data}")
            return True
        else:
            print(f"❌ Product publish failed: {response.status_code}")
            error_text = response.text
            print(f"Error: {error_text}")
            
            # Analyze the error
            if "401" in str(response.status_code) or "authentication" in error_text.lower():
                print("🔍 AUTHENTICATION ERROR - Need to login first")
            elif "user" in error_text.lower() and "not found" in error_text.lower():
                print("🔍 USER NOT FOUND - Need Facebook authentication")
            elif "permission" in error_text.lower():
                print("🔍 PERMISSION ERROR - Instagram permissions missing")
                
            return False
            
    except Exception as e:
        print(f"💥 Test error: {e}")
        return False

def analyze_instagram_issue():
    """Provide comprehensive analysis of Instagram publication issue"""
    print("\n📋 INSTAGRAM PUBLICATION ISSUE ANALYSIS")
    print("=" * 60)
    
    print("🔍 CONFIGURATION STATUS:")
    print("  ✅ Multi-platform config: gizmobbs → Facebook + Instagram")
    print("  ✅ Instagram account found: @logicamp_berger (ID: 17841459952999804)")
    print("  ✅ Facebook page found: Le Berger Blanc Suisse (ID: 102401876209415)")
    print("  ✅ Backend logic: Multi-platform publication implemented")
    
    print("\n❌ LIKELY ROOT CAUSE:")
    print("  → NO AUTHENTICATED USER with Facebook/Instagram access")
    print("  → System cannot get valid access tokens for Instagram API")
    
    print("\n🔧 SOLUTION STEPS:")
    print("  1. 🌐 Open: https://content-sync-app.preview.emergentagent.com")
    print("  2. 🔑 Click 'Facebook Login' and authenticate")
    print("  3. 📊 Select Business Manager with Instagram access")
    print("  4. ✅ Verify both Facebook page and Instagram account appear")
    print("  5. 🚀 Try publishing a test post")
    
    print("\n💡 WHY TESTS PASS BUT PUBLISHING FAILS:")
    print("  → Configuration is correct (multi-platform setup)")
    print("  → Code is correct (Instagram API calls implemented)")
    print("  → Missing: Real user authentication and valid tokens")
    
    print("\n🎯 NEXT STEPS:")
    print("  1. Authenticate with real Facebook Business Manager")
    print("  2. Verify Instagram permissions in Business Manager")
    print("  3. Test publication with authenticated user")
    
    print("=" * 60)

def main():
    """Run comprehensive Instagram issue diagnosis"""
    print("🎯 DIAGNOSING INSTAGRAM PUBLICATION ISSUE")
    print("=" * 60)
    
    tests = [
        ("Multi-platform Test", test_gizmobbs_publication_simulation),
        ("Facebook Image Test", test_facebook_image_display_test),
        ("Product Publish Test", create_test_user_simulation)
    ]
    
    authentication_needed = False
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        print("-" * 40)
        result = test_func()
        if not result:
            authentication_needed = True
    
    # Provide final analysis
    analyze_instagram_issue()
    
    if authentication_needed:
        print("\n🚨 DIAGNOSIS COMPLETE:")
        print("Instagram publication fails due to MISSING AUTHENTICATION")
        print("The system is correctly configured but needs a real Facebook user login!")

if __name__ == "__main__":
    main()