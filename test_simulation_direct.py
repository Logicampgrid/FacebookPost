#!/usr/bin/env python3
"""
Direct test of the simulation function to verify our enhancements
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append('/app/backend')

from server import simulate_facebook_post_for_test, Post
from datetime import datetime

async def test_direct_simulation():
    """Test the simulation function directly"""
    print("🧪 DIRECT SIMULATION TEST")
    print("=" * 50)
    
    # Test with gizmobbs video
    print("\n1. Testing GIZMOBBS VIDEO simulation:")
    
    # Create a video post for gizmobbs
    video_post = Post(
        id="test-video-123",
        user_id="test-user",
        content="Test vidéo gizmobbs avec commentaire auto",
        media_urls=["/api/uploads/test_video.mp4"],  # .mp4 will be detected as video
        link_metadata=[{"url": "https://logicamp.org/werdpress/gizmobbs/test-video"}],
        target_type="page",
        target_id="102401876209415",
        target_name="Le Berger Blanc Suisse",
        platform="facebook",
        status="pending",
        created_at=datetime.utcnow(),
        published_at=None
    )
    
    result = await simulate_facebook_post_for_test(
        video_post, 
        "test_token_123", 
        shop_type="gizmobbs"
    )
    
    print(f"Result: {result}")
    
    if result and result.get("enhanced_features", {}).get("gizmobbs_video_comment"):
        print("✅ GIZMOBBS video comment feature working!")
    else:
        print("❌ GIZMOBBS video comment feature not working")
    
    print("\n2. Testing ENHANCED CLICKABLE IMAGE simulation:")
    
    # Test enhanced clickable images
    image_post = Post(
        id="test-image-123",
        user_id="test-user", 
        content="Test image cliquable améliorée",
        media_urls=["/api/uploads/test_image.jpg"],  # .jpg will be detected as image
        link_metadata=[{"url": "https://logicamp.org/werdpress/gizmobbs/test-image"}],
        target_type="page",
        target_id="102401876209415",
        target_name="Le Berger Blanc Suisse",
        platform="facebook",
        status="pending",
        created_at=datetime.utcnow(),
        published_at=None
    )
    
    result = await simulate_facebook_post_for_test(
        image_post,
        "test_token_456",
        shop_type="gizmobbs"
    )
    
    print(f"Result: {result}")
    
    if result and result.get("enhanced_features", {}).get("clickable_image_configured"):
        print("✅ Enhanced clickable images working!")
    else:
        print("❌ Enhanced clickable images not working")
    
    print("\n3. Testing NON-GIZMOBBS (should not have gizmobbs comment):")
    
    result = await simulate_facebook_post_for_test(
        video_post,
        "test_token_789", 
        shop_type="outdoor"  # Different store
    )
    
    print(f"Result: {result}")
    
    if not result.get("enhanced_features", {}).get("gizmobbs_video_comment"):
        print("✅ Non-gizmobbs correctly does not have gizmobbs comment!")
    else:
        print("❌ Non-gizmobbs incorrectly has gizmobbs comment")

if __name__ == "__main__":
    asyncio.run(test_direct_simulation())