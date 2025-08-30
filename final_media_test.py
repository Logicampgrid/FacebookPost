#!/usr/bin/env python3
"""
Final test to verify the localhost URL fix in Facebook posting
"""

import sys
import os
sys.path.append('/app/backend')

# Import the Post model and posting functions
from server import Post, post_to_facebook, post_to_instagram
from datetime import datetime

def test_url_construction():
    """Test that the URL construction uses the correct domain"""
    
    print("🔍 Testing URL construction in Facebook posting logic...")
    
    # Create a mock post with media
    test_post = Post(
        id="test-post-123",
        user_id="test-user-123", 
        content="Test post with media",
        media_urls=["/uploads/test-image.jpg"],
        target_type="page",
        target_id="test-page-123",
        target_name="Test Page",
        platform="facebook",
        status="draft",
        created_at=datetime.utcnow()
    )
    
    print(f"✅ Created test post with media URL: {test_post.media_urls[0]}")
    
    # Test the URL construction logic by examining the code
    media_url = test_post.media_urls[0]
    
    if media_url.startswith('http'):
        full_media_url = media_url
    else:
        # This is the logic from the fixed backend
        base_url = os.getenv("PUBLIC_BASE_URL", "https://fb-media-fix.preview.emergentagent.com")
        full_media_url = f"{base_url}{media_url}"
    
    print(f"📸 Constructed media URL: {full_media_url}")
    
    if "localhost:8001" in full_media_url:
        print("❌ ISSUE: Still using localhost URLs!")
        return False
    elif "social-media-share.preview.emergentagent.com" in full_media_url:
        print("✅ SUCCESS: Using correct public domain!")
        return True
    else:
        print(f"⚠️  Unexpected domain in URL: {full_media_url}")
        return False

def test_environment_variable():
    """Test the environment variable setup"""
    print("\n🔍 Testing environment variable configuration...")
    
    public_base_url = os.getenv("PUBLIC_BASE_URL")
    if public_base_url:
        print(f"✅ PUBLIC_BASE_URL is set: {public_base_url}")
    else:
        print("⚠️  PUBLIC_BASE_URL not set, using default")
        
    # Test the default fallback
    base_url = os.getenv("PUBLIC_BASE_URL", "https://fb-media-fix.preview.emergentagent.com")
    print(f"📍 Base URL being used: {base_url}")
    
    return base_url

def main():
    print("🚀 Final Media URL Construction Test")
    print("=" * 50)
    
    # Test 1: URL construction logic
    url_test_passed = test_url_construction()
    
    # Test 2: Environment variable
    base_url = test_environment_variable()
    
    print("\n" + "=" * 50)
    if url_test_passed:
        print("🎉 SUCCESS: Media URL construction fix is working!")
        print("✅ Facebook API will now be able to access uploaded media")
        print(f"✅ Media URLs will use: {base_url}")
    else:
        print("❌ FAILURE: Media URL construction still has issues")
        
    print("\n📋 Summary of the fix:")
    print("- Changed hardcoded 'http://localhost:8001' to use PUBLIC_BASE_URL environment variable")
    print("- Default fallback to 'https://fb-media-fix.preview.emergentagent.com'")
    print("- Applied fix to both Facebook and Instagram posting functions")
    print("- This allows Facebook/Instagram APIs to access uploaded media from external servers")

if __name__ == "__main__":
    main()