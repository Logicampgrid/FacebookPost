#!/usr/bin/env python3
"""
Direct test of the Facebook posting function logic
"""

import requests
import json
import uuid
import io

def test_facebook_posting_logic():
    base_url = "https://upload-guard.preview.emergentagent.com"
    
    print("🔍 Testing Facebook posting logic directly...")
    
    # Create a post with media
    test_user_id = str(uuid.uuid4())
    
    # Step 1: Create post
    form_data = {
        "content": "Direct test of Facebook posting with media",
        "target_type": "page", 
        "target_id": "test_page_123",
        "target_name": "Test Page",
        "platform": "facebook",
        "user_id": test_user_id
    }
    
    response = requests.post(f"{base_url}/api/posts", data=form_data)
    if response.status_code != 200:
        print(f"❌ Failed to create post: {response.status_code}")
        return
        
    post_data = response.json()
    post_id = post_data["post"]["id"]
    print(f"✅ Created post: {post_id}")
    
    # Step 2: Upload media
    test_image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01IEND\xaeB`\x82'
    
    files = {
        'file': ('test_media.png', io.BytesIO(test_image_content), 'image/png')
    }
    
    response = requests.post(f"{base_url}/api/posts/{post_id}/media", files=files)
    if response.status_code != 200:
        print(f"❌ Failed to upload media: {response.status_code}")
        return
        
    media_data = response.json()
    print(f"✅ Uploaded media: {media_data['url']}")
    
    # Step 3: Try to publish (this will trigger the Facebook posting logic)
    print("🔍 Attempting to publish (will fail but show URL construction)...")
    
    response = requests.post(f"{base_url}/api/posts/{post_id}/publish")
    print(f"Publish response status: {response.status_code}")
    
    if response.status_code == 500:
        error_data = response.json()
        print(f"Error detail: {error_data.get('detail', 'No detail')}")
    
    # Check backend logs to see what URL was constructed
    print("✅ Check backend logs to see the URL construction")

if __name__ == "__main__":
    test_facebook_posting_logic()