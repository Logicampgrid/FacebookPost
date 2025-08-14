#!/usr/bin/env python3
"""
Test script pour tester les fonctionnalités avec un token Facebook réel
"""

import requests
import json
import sys
import os

API_BASE = "http://localhost:8001"

def test_clickable_post_direct(access_token):
    """Test direct de publication avec image cliquable"""
    print(f"🔗 Testing clickable image post with token...")
    
    # Créer un post directement via l'API
    post_data = {
        "content": "🧪 Test image cliquable - Cliquez sur l'image pour voir le produit !",
        "target_type": "page",
        "target_id": "102401876209415",  # Le Berger Blanc Suisse
        "target_name": "Le Berger Blanc Suisse", 
        "platform": "facebook",
        "comment_link": "https://logicampoutdoor.com/product/test-clickable-123"
    }
    
    # Ajouter un fichier image existant
    files = {
        'file': open('/app/backend/test_image.jpg', 'rb') if os.path.exists('/app/backend/test_image.jpg') else None
    }
    if not files['file']:
        print("❌ No test image found")
        return False
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/posts", 
                               data=post_data, 
                               files=files,
                               headers=headers,
                               timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📋 Response: {response.text[:500]}...")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ Clickable image post creation successful!")
            return True
        else:
            print(f"❌ Clickable image post failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing clickable post: {e}")
        return False
    finally:
        if files['file']:
            files['file'].close()

def test_instagram_post_direct(access_token):
    """Test direct de publication Instagram"""
    print(f"📱 Testing Instagram post with token...")
    
    post_data = {
        "content": "🧪 Test Instagram - Publication automatique depuis l'API ! 📸 #test #api",
        "target_type": "instagram",
        "target_id": "17841459952999804",  # logicamp_berger
        "target_name": "logicamp_berger",
        "platform": "instagram"
    }
    
    files = {
        'file': open('/app/backend/test_image.jpg', 'rb') if os.path.exists('/app/backend/test_image.jpg') else None
    }
    if not files['file']:
        print("❌ No test image found")
        return False
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.post(f"{API_BASE}/api/posts",
                               data=post_data,
                               files=files, 
                               headers=headers,
                               timeout=30)
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📋 Response: {response.text[:500]}...")
        
        if response.status_code == 200 or response.status_code == 201:
            print("✅ Instagram post creation successful!")
            return True
        else:
            print(f"❌ Instagram post failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Instagram post: {e}")
        return False
    finally:
        if files['file']:
            files['file'].close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_with_token.py <facebook_access_token>")
        print("\nTo get a token:")
        print("1. Go to https://developers.facebook.com/tools/explorer/")
        print("2. Select App ID: 5664227323683118")
        print("3. Generate User Access Token with permissions:")
        print("   - pages_manage_posts")
        print("   - pages_read_engagement") 
        print("   - pages_show_list")
        print("   - business_management")
        print("   - instagram_content_publish")
        return
    
    access_token = sys.argv[1]
    
    print("🧪 TESTING FACEBOOK & INSTAGRAM FUNCTIONALITY")
    print("=" * 60)
    
    # Test clickable images
    clickable_ok = test_clickable_post_direct(access_token)
    
    print("\n" + "-" * 40 + "\n")
    
    # Test Instagram
    instagram_ok = test_instagram_post_direct(access_token)
    
    print("\n📊 TEST RESULTS")
    print("=" * 30)
    print(f"🔗 Clickable Images: {'✅ WORKING' if clickable_ok else '❌ FAILED'}")
    print(f"📱 Instagram Posts: {'✅ WORKING' if instagram_ok else '❌ FAILED'}")
    
    if not clickable_ok or not instagram_ok:
        print("\n🔧 TROUBLESHOOTING TIPS:")
        print("- Verify Facebook token has all required permissions")
        print("- Check that Instagram account is connected to Facebook page")
        print("- Ensure Instagram account is a Business account")
        print("- Check backend logs for detailed error messages")

if __name__ == "__main__":
    main()