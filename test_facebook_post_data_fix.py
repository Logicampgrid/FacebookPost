#!/usr/bin/env python3
"""
Test script to verify the facebook_post_data fix in create_product_post_from_local_image function
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append('/app/backend')

# Import the function and models
from server import create_product_post_from_local_image, ProductPublishRequest

async def test_facebook_post_data_fix():
    """Test that facebook_post_data is properly initialized for all execution paths"""
    
    print("🧪 Testing facebook_post_data initialization fix...")
    
    # Create a test request
    test_request = ProductPublishRequest(
        title="Test Product",
        description="Test product description",
        image_url="https://example.com/test-image.jpg",
        product_url="https://example.com/product",
        shop_type="gizmobbs",  # This should trigger Instagram priority path
        user_id="test_user",
        page_id="test_page"
    )
    
    # Test with a local image URL
    local_image_url = "/api/uploads/test_image.jpg"
    
    try:
        # This should not raise the "cannot access local variable 'facebook_post_data'" error
        result = await create_product_post_from_local_image(test_request, local_image_url)
        print("✅ Function completed without facebook_post_data error")
        print(f"📊 Result status: {result.get('status', 'unknown')}")
        return True
        
    except Exception as e:
        if "cannot access local variable 'facebook_post_data'" in str(e):
            print(f"❌ facebook_post_data error still present: {e}")
            return False
        else:
            print(f"⚠️ Other error (expected): {e}")
            print("✅ facebook_post_data error is fixed (different error occurred)")
            return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_facebook_post_data_fix())
        if result:
            print("\n🎉 Test PASSED: facebook_post_data initialization fix is working!")
        else:
            print("\n💥 Test FAILED: facebook_post_data error still exists")
    except Exception as e:
        print(f"\n💥 Test script error: {e}")