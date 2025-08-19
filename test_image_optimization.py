#!/usr/bin/env python3
"""
Test script to verify image optimization for Instagram
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append('/app/backend')

# Import the optimization function
from server import optimize_image_for_instagram

def test_image_optimization():
    """Test that image optimization works properly"""
    
    print("🧪 Testing Instagram image optimization...")
    
    # Use the actual image that was failing
    test_image_path = "/app/backend/uploads/webhook_7e59092f_1755641963.jpg"
    optimized_path = "/app/backend/uploads/test_optimized.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return False
    
    print(f"📁 Original image: {test_image_path}")
    print(f"📊 Original size: {os.path.getsize(test_image_path)} bytes")
    
    try:
        # Test the optimization function
        result = optimize_image_for_instagram(test_image_path, optimized_path)
        
        if result:
            print("✅ Image optimization successful")
            if os.path.exists(optimized_path):
                print(f"📁 Optimized image: {optimized_path}")
                print(f"📊 Optimized size: {os.path.getsize(optimized_path)} bytes")
                
                # Clean up test file
                os.remove(optimized_path)
                return True
            else:
                print("❌ Optimized image was not created")
                return False
        else:
            print("❌ Image optimization failed")
            return False
            
    except Exception as e:
        print(f"💥 Error during optimization: {e}")
        return False

if __name__ == "__main__":
    try:
        result = test_image_optimization()
        if result:
            print("\n🎉 Image optimization test PASSED!")
        else:
            print("\n💥 Image optimization test FAILED!")
    except Exception as e:
        print(f"\n💥 Test script error: {e}")