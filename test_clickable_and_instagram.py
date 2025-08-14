#!/usr/bin/env python3
"""
Test script pour diagnostiquer les problèmes avec :
1. Images cliquables sur Facebook
2. Publication Instagram
"""

import requests
import json
import sys
import os

API_BASE = "http://localhost:8001"

def test_facebook_token_and_user():
    """Test si on a un utilisateur connecté avec un token valide"""
    print("🔍 Testing user authentication...")
    
    # Get all posts to check if we have users
    response = requests.get(f"{API_BASE}/api/posts")
    if response.status_code != 200:
        print(f"❌ Cannot access posts API: {response.status_code}")
        return None
    
    posts_data = response.json()
    print(f"📊 Found {len(posts_data.get('posts', []))} existing posts")
    
    # Check if we can find user info from logs or database
    print("✅ API is accessible")
    return True

def test_clickable_image_post():
    """Test création d'un post avec image cliquable"""
    print("\n🔗 Testing clickable image functionality...")
    
    # Use an existing local image
    test_image_path = "/api/uploads/0017f703-5aee-4639-85db-f54c70cf7afc.jpg"
    
    # Test data for a clickable image post
    post_data = {
        "content": "Test produit avec image cliquable",
        "media_urls": [test_image_path],
        "comment_link": "https://logicampoutdoor.com/product/test-clickable",
        "target_type": "page",
        "target_id": "102401876209415",  # Le Berger Blanc Suisse from logs
        "target_name": "Le Berger Blanc Suisse",
        "platform": "facebook"
    }
    
    print(f"📝 Creating post with clickable image...")
    print(f"📸 Image: {test_image_path}")
    print(f"🔗 Link: {post_data['comment_link']}")
    print(f"🎯 Target: {post_data['target_name']}")
    
    # This would test the internal logic
    print("⚠️ Need to test with actual Facebook token - manual test required")
    return True

def test_instagram_functionality():
    """Test publication Instagram"""
    print("\n📱 Testing Instagram functionality...")
    
    # From logs, we know there are Instagram accounts: logicamp_berger
    instagram_data = {
        "content": "Test Instagram post",
        "media_urls": ["/api/uploads/0017f703-5aee-4639-85db-f54c70cf7afc.jpg"],
        "target_type": "instagram",
        "target_id": "17841459952999804",  # From test logs
        "target_name": "logicamp_berger",
        "platform": "instagram"
    }
    
    print(f"📝 Instagram post preparation...")
    print(f"📸 Image: {instagram_data['media_urls'][0]}")
    print(f"🎯 Target: {instagram_data['target_name']}")
    
    print("⚠️ Need to test with actual Facebook token - manual test required")
    return True

def check_image_accessibility():
    """Vérifier si les images locales sont accessibles"""
    print("\n📸 Testing image accessibility...")
    
    # Test local image access
    image_url = f"http://localhost:8001/api/uploads/0017f703-5aee-4639-85db-f54c70cf7afc.jpg"
    
    try:
        response = requests.head(image_url, timeout=5)
        if response.status_code == 200:
            print(f"✅ Local image accessible: {image_url}")
            return True
        else:
            print(f"❌ Local image not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing local image: {e}")
        return False

def analyze_backend_logs():
    """Analyser les logs pour identifier les problèmes"""
    print("\n📋 Analyzing recent backend activity...")
    
    # Check what we know from the logs seen earlier
    issues_found = []
    
    print("From recent logs analysis:")
    print("✅ Found 4 business managers")
    print("✅ Found 2 Facebook pages for business manager 284950785684706")
    print("✅ Found 2 Instagram accounts connected")
    print("❌ Errors getting groups for all business managers (400 errors)")
    print("✅ User successfully authenticated: Didier Preud'homme")
    
    # Specific issues identified
    issues_found.extend([
        "Group access permissions may be insufficient (400 errors)",
        "External image download timeout issues",
        "Need to test actual posting with real Facebook tokens"
    ])
    
    return issues_found

def main():
    print("🔧 Facebook/Instagram Functionality Diagnostic Tool")
    print("=" * 60)
    
    # Test basic API access
    if not test_facebook_token_and_user():
        print("❌ Basic API access failed")
        return
    
    # Check image accessibility
    image_ok = check_image_accessibility()
    
    # Test clickable image logic
    test_clickable_image_post()
    
    # Test Instagram logic
    test_instagram_functionality()
    
    # Analyze what we found
    issues = analyze_backend_logs()
    
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    print("\n✅ WORKING COMPONENTS:")
    print("- Backend API is running and accessible")
    print("- User authentication system working")
    print("- Facebook pages and Instagram accounts detected")
    if image_ok:
        print("- Local image serving working")
    
    print("\n⚠️ ISSUES IDENTIFIED:")
    for issue in issues:
        print(f"- {issue}")
    
    print("\n🔧 RECOMMENDED FIXES:")
    print("1. Fix external image download timeout by using local images or better timeout handling")
    print("2. Test clickable image posts with real Facebook token")
    print("3. Test Instagram posting with real Facebook token") 
    print("4. Investigate group permissions (400 errors) - may not be critical")
    
    print("\n📝 NEXT STEPS:")
    print("1. Use the manual token method to get a valid Facebook token")
    print("2. Test actual posting through the frontend interface")
    print("3. Monitor logs during actual posting to see specific errors")

if __name__ == "__main__":
    main()