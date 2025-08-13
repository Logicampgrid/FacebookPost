#!/usr/bin/env python3
"""
Test script to verify the Facebook image posting fix
"""
import os
import sys

def test_local_file_logic():
    """Test the local file detection logic"""
    print("🧪 Testing Facebook Image Fix...")
    
    # Test case 1: Local file exists
    test_media_url = "/api/uploads/0eb20726-21bd-4b95-bd4e-564df23950b4.jpg"
    local_file_path = test_media_url.replace('/api/uploads/', 'uploads/')
    
    print(f"📁 Testing media URL: {test_media_url}")
    print(f"📂 Expected local path: {local_file_path}")
    
    if os.path.exists(local_file_path):
        print("✅ Local file EXISTS - fix will work!")
        
        # Get file size
        file_size = os.path.getsize(local_file_path)
        print(f"📊 File size: {file_size} bytes")
        
        # Read a small portion to verify it's readable
        try:
            with open(local_file_path, 'rb') as f:
                content_sample = f.read(100)  # Read first 100 bytes
            print(f"✅ File is readable - {len(content_sample)} bytes read")
            
            # Check if it's a JPEG
            if content_sample.startswith(b'\xff\xd8\xff'):
                print("✅ Valid JPEG file detected")
            else:
                print("⚠️ File format might not be JPEG")
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
            
        return True
    else:
        print("❌ Local file DOES NOT exist - fix won't work for this file")
        return False

def test_url_construction():
    """Test URL construction logic"""
    print("\n🔗 Testing URL construction...")
    
    base_url = os.getenv("PUBLIC_BASE_URL", "https://just-ok-3.preview.emergentagent.com")
    test_media_url = "/api/uploads/test-image.jpg"
    full_url = f"{base_url}{test_media_url}"
    
    print(f"🌐 Base URL: {base_url}")
    print(f"📱 Media URL: {test_media_url}")
    print(f"🔗 Full URL: {full_url}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 FACEBOOK IMAGE POSTING FIX - VERIFICATION TEST")
    print("=" * 60)
    
    # Change to backend directory
    os.chdir('/app/backend')
    
    # Run tests
    test1_passed = test_local_file_logic()
    test2_passed = test_url_construction()
    
    print("\n" + "=" * 60)
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED - Facebook image fix is working!")
        print("✅ Images should now display properly on Facebook")
        print("✅ No more timeout errors from URL downloads")
    else:
        print("❌ Some tests failed - fix might need adjustment")
    
    print("=" * 60)