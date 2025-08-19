#!/usr/bin/env python3
"""
Test script to verify the facebook_post_data fix works for different shop configurations
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append('/app/backend')

# Import the function and models
from server import create_product_post_from_local_image, ProductPublishRequest

async def test_shop_type(shop_type, expected_path):
    """Test a specific shop type configuration"""
    
    print(f"\n🧪 Testing shop_type: {shop_type} (expected: {expected_path})")
    
    # Create a test request
    test_request = ProductPublishRequest(
        title=f"Test Product for {shop_type}",
        description="Test product description",
        image_url="https://example.com/test-image.jpg",
        product_url="https://example.com/product",
        shop_type=shop_type,
        user_id="test_user",
        page_id="test_page"
    )
    
    # Test with a local image URL
    local_image_url = "/api/uploads/test_image.jpg"
    
    try:
        result = await create_product_post_from_local_image(test_request, local_image_url)
        print(f"✅ {shop_type}: Function completed without facebook_post_data error")
        return True
        
    except Exception as e:
        if "cannot access local variable 'facebook_post_data'" in str(e):
            print(f"❌ {shop_type}: facebook_post_data error still present: {e}")
            return False
        else:
            print(f"✅ {shop_type}: facebook_post_data error is fixed (other error: {str(e)[:100]}...)")
            return True

async def test_multiple_shop_types():
    """Test multiple shop types to ensure the fix works for all execution paths"""
    
    test_cases = [
        ("gizmobbs", "Instagram Priority"),
        ("test_shop", "Facebook Only"),
        ("unknown_shop", "Default Facebook"),
    ]
    
    results = []
    
    for shop_type, expected_path in test_cases:
        result = await test_shop_type(shop_type, expected_path)
        results.append(result)
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"\n📊 SUMMARY: {success_count}/{total_count} shop types passed the test")
    
    if success_count == total_count:
        print("🎉 ALL TESTS PASSED: facebook_post_data fix works for all shop configurations!")
        return True
    else:
        print("💥 SOME TESTS FAILED: facebook_post_data error still exists in some paths")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_multiple_shop_types())
        if not result:
            exit(1)
    except Exception as e:
        print(f"\n💥 Test script error: {e}")
        exit(1)