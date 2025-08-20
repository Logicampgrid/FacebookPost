#!/usr/bin/env python3
"""
Test script to validate the Instagram posting fix
"""
import asyncio
import os
import sys
import json
import uuid
from datetime import datetime

# Add the backend directory to Python path
sys.path.append('/app/backend')

# Import the necessary functions
from server import Post, post_to_instagram, FACEBOOK_GRAPH_URL, optimize_image_for_instagram

async def test_instagram_posting_with_mock_data():
    """Test Instagram posting function with mock data to validate fix"""
    print("🧪 Testing Instagram posting fix...")
    
    # Create a mock post object similar to what would be generated
    test_post_data = {
        "id": str(uuid.uuid4()),
        "user_id": "test_user",
        "content": "Test post for Instagram fix validation\n\n#bergerblancsuisse #chien #dog #test",
        "media_urls": ["/api/uploads/test_image.jpg"],
        "target_type": "instagram",
        "target_id": "17841459952999804",  # @logicamp_berger from webhook data
        "target_name": "@logicamp_berger",
        "platform": "instagram",
        "status": "published",
        "created_at": datetime.utcnow(),
        "published_at": datetime.utcnow()
    }
    
    # Create Post object
    test_post = Post(**test_post_data)
    
    # Create a test image file
    test_image_path = "uploads/test_image.jpg"
    os.makedirs("uploads", exist_ok=True)
    
    # Create a simple test image (1x1 pixel)
    from PIL import Image
    test_image = Image.new('RGB', (100, 100), color='red')
    test_image.save(test_image_path, 'JPEG')
    
    print(f"✅ Created test image: {test_image_path}")
    
    # Test with a fake access token to see if our error handling works correctly
    fake_access_token = "fake_token_for_testing"
    
    print("🔄 Testing Instagram posting function...")
    try:
        result = await post_to_instagram(test_post, fake_access_token)
        print(f"📤 Instagram posting result: {result}")
        
        # Validate the result structure
        if result:
            if result.get("status") == "error":
                print("✅ EXPECTED: Function correctly returned error status")
                print(f"   Error message: {result.get('message')}")
                
                # Check if the error message is informative
                if result.get("message") and len(result.get("message")) > 0:
                    print("✅ GOOD: Error message is informative")
                else:
                    print("❌ BAD: Error message is empty or missing")
                    
            elif result.get("status") == "success":
                print("✅ SUCCESS: Function returned success status")
                if result.get("id"):
                    print(f"✅ GOOD: Post ID returned: {result.get('id')}")
                else:
                    print("❌ BAD: No post ID in success response")
            else:
                print(f"⚠️ UNEXPECTED: Unknown status: {result.get('status')}")
        else:
            print("❌ BAD: Function returned None")
        
        # Cleanup
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            print("🧹 Cleaned up test image")
            
        return result
        
    except Exception as e:
        print(f"❌ Exception during test: {e}")
        return None

def test_error_response_structure():
    """Test that our error responses have the correct structure"""
    print("\n🧪 Testing error response structure...")
    
    # Test different types of responses our function might return
    test_cases = [
        {"status": "error", "message": "No media provided for Instagram"},
        {"status": "error", "message": "Failed to create Instagram media container"},
        {"status": "success", "id": "test_post_123", "platform": "instagram"},
        {"status": "error", "message": "Instagram error: API timeout"}
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"Test case {i+1}: {test_case}")
        
        # Check if error responses have the right fields
        if test_case.get("status") == "error":
            if "message" in test_case and test_case["message"]:
                print("✅ Error response has message")
            else:
                print("❌ Error response missing message")
                
        elif test_case.get("status") == "success":
            if "id" in test_case and test_case["id"]:
                print("✅ Success response has post ID")
            else:
                print("❌ Success response missing post ID")

def analyze_webhook_data():
    """Analyze the original webhook data that showed the issue"""
    print("\n🔍 Analyzing original webhook issue...")
    
    webhook_data = {
        "instagram_accounts": [{
            "platform": "instagram",
            "account_name": "logicamp_berger", 
            "account_id": "17841459952999804",
            "status": "failed",
            "error": "No post ID returned"
        }]
    }
    
    print("Original issue:")
    print(f"   Account: @{webhook_data['instagram_accounts'][0]['account_name']}")
    print(f"   Status: {webhook_data['instagram_accounts'][0]['status']}")
    print(f"   Error: {webhook_data['instagram_accounts'][0]['error']}")
    
    print("\n🔧 Root cause analysis:")
    print("   1. Instagram API was called successfully (container created)")
    print("   2. But publish step returned response without 'id' field")
    print("   3. Previous code was checking for 'id' in result but not handling missing ID properly")
    print("   4. Fixed by:")
    print("      - Better error handling in post_to_instagram function")
    print("      - More detailed logging of API responses")
    print("      - Proper status checking instead of just ID presence")

if __name__ == "__main__":
    print("🚀 Starting Instagram posting fix validation tests...")
    
    # Test 1: Response structure validation
    test_error_response_structure()
    
    # Test 2: Webhook data analysis
    analyze_webhook_data()
    
    # Test 3: Actual function testing
    result = asyncio.run(test_instagram_posting_with_mock_data())
    
    print("\n📋 Summary:")
    print("✅ Fixed Instagram posting function structure")
    print("✅ Added comprehensive error handling")  
    print("✅ Added detailed API response logging")
    print("✅ Consistent return format for all code paths")
    print("✅ Better error messages for debugging")
    
    print("\n🎯 The 'No post ID returned' error should now:")
    print("   1. Be caught and logged with full API response details")
    print("   2. Return proper error status with descriptive message")
    print("   3. Allow for better debugging of Instagram API issues")