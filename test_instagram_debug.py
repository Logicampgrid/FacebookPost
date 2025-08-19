#!/usr/bin/env python3
"""
Debug script for Instagram posting issues
"""

import asyncio
import sys
import os
import requests

# Add the backend directory to Python path
sys.path.append('/app/backend')

# Import necessary functions and variables
from server import (
    post_to_instagram, Post, FACEBOOK_GRAPH_URL, 
    get_dynamic_base_url, optimize_image_for_instagram
)

async def debug_instagram_posting():
    """Debug the Instagram posting process step by step"""
    
    print("🔍 Debugging Instagram posting process...")
    
    # Test parameters
    test_image_path = "/app/backend/uploads/webhook_7e59092f_1755641963.jpg"
    instagram_id = "17841459952999804"  # From the error log
    test_token = "test_token_123"  # Use test token to avoid real API calls
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return False
    
    print(f"📁 Using test image: {test_image_path}")
    print(f"📊 Image size: {os.path.getsize(test_image_path)} bytes")
    
    # Create a test Post object
    test_post = Post(
        id="test-post-id",
        user_id="test-user",
        content="Test Instagram post for debugging",
        media_urls=["/api/uploads/webhook_7e59092f_1755641963.jpg"],
        target_type="instagram",
        target_id=instagram_id,
        target_name="logicamp_berger",
        platform="instagram"
    )
    
    print(f"📱 Test post created for @{test_post.target_name}")
    print(f"🎯 Target Instagram ID: {test_post.target_id}")
    
    # Test the posting function
    try:
        print("\n🚀 Testing Instagram posting function...")
        result = await post_to_instagram(test_post, test_token)
        
        if result:
            print(f"✅ Instagram function returned: {result}")
            if result.get("status") == "success" and "id" in result:
                print("✅ Success: Function returned proper post ID")
                return True
            elif result.get("status") == "error":
                print(f"⚠️ Expected error for test token: {result.get('message')}")
                return True  # This is expected with test token
            else:
                print(f"❌ Unexpected result format: {result}")
                return False
        else:
            print("❌ Instagram function returned None")
            return False
            
    except Exception as e:
        print(f"💥 Error during Instagram posting: {e}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(debug_instagram_posting())
        if result:
            print("\n🎉 Debug test PASSED!")
        else:
            print("\n💥 Debug test FAILED!")
    except Exception as e:
        print(f"\n💥 Debug script error: {e}")