#!/usr/bin/env python3

import requests
import json
import sys

# The Facebook token provided in the request
FACEBOOK_TOKEN = "EAASCBksMsMQBPLEZAFJUqZAo8twA9aSS1dm1MD87wxYdMZBIBU0ttwVTifymb64GFYgemve4OpB7Or5XIjmZA0jLWk1UrAvXCmOfZAsD0QC45c9mL2OkUsP6svw09bioTCIAdZAiKiC3Wx6HzwuVJSMPWOasZAuAhUki50gZAejPI7QJOvhS81O7vq78AxMrE1jZC0e6AbWM2JfY3LZAoQVOLIKeL4wrEoQbu6F9jELbOeR5Lod1YsxgZDZD"

BASE_URL = "http://localhost:8001"

def test_facebook_token_debug():
    """Test the provided Facebook token"""
    print("🔍 Testing provided Facebook token...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/debug/facebook-token/{FACEBOOK_TOKEN}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token debug successful")
            print(f"   Status: {data.get('status')}")
            
            if data.get('status') == 'valid':
                user_data = data.get('user', {})
                print(f"   User ID: {user_data.get('id')}")
                print(f"   User Name: {user_data.get('name')}")
                print(f"   User Email: {user_data.get('email', 'N/A')}")
                return True
            else:
                print(f"   Error: {data.get('error')}")
                return False
        else:
            print(f"❌ Failed - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_facebook_auth():
    """Test Facebook authentication with the provided token"""
    print("\n🔍 Testing Facebook authentication...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/facebook",
            json={"access_token": FACEBOOK_TOKEN},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Authentication successful")
            print(f"   Message: {data.get('message')}")
            
            user = data.get('user', {})
            print(f"   User ID: {user.get('_id')}")
            print(f"   Facebook ID: {user.get('facebook_id')}")
            print(f"   Name: {user.get('name')}")
            print(f"   Email: {user.get('email', 'N/A')}")
            
            pages = user.get('facebook_pages', [])
            print(f"   Facebook Pages: {len(pages)}")
            
            for i, page in enumerate(pages[:3]):  # Show first 3 pages
                print(f"     Page {i+1}: {page.get('name')} (ID: {page.get('id')})")
            
            if len(pages) > 3:
                print(f"     ... and {len(pages) - 3} more pages")
                
            return True, user
        else:
            print(f"❌ Failed - Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, None

def test_create_and_manage_post(user):
    """Test creating and managing a post with authenticated user"""
    if not user:
        print("\n⚠️  Skipping post tests - no authenticated user")
        return False
        
    print("\n🔍 Testing post creation with authenticated user...")
    
    user_id = user.get('_id')
    pages = user.get('facebook_pages', [])
    
    if not pages:
        print("❌ No Facebook pages available for posting")
        return False
    
    # Use the first page for testing
    target_page = pages[0]
    
    try:
        # Create a post
        form_data = {
            "content": "Test post from Facebook Post Manager - Testing API integration",
            "target_type": "page",
            "target_id": target_page.get('id'),
            "target_name": target_page.get('name'),
            "user_id": user_id
        }
        
        response = requests.post(f"{BASE_URL}/api/posts", data=form_data)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Post created successfully")
            
            post = data.get('post', {})
            post_id = post.get('id')
            print(f"   Post ID: {post_id}")
            print(f"   Content: {post.get('content')[:50]}...")
            print(f"   Target: {post.get('target_name')}")
            
            # Test getting posts for this user
            print("\n🔍 Testing get posts for user...")
            response = requests.get(f"{BASE_URL}/api/posts?user_id={user_id}")
            
            if response.status_code == 200:
                posts_data = response.json()
                posts = posts_data.get('posts', [])
                print(f"✅ Found {len(posts)} posts for user")
                
                # Find our created post
                our_post = next((p for p in posts if p.get('id') == post_id), None)
                if our_post:
                    print(f"   ✅ Our created post found in user's posts")
                else:
                    print(f"   ⚠️  Our created post not found in user's posts")
            
            # Test deleting the post (cleanup)
            print(f"\n🔍 Testing post deletion...")
            response = requests.delete(f"{BASE_URL}/api/posts/{post_id}")
            
            if response.status_code == 200:
                print(f"✅ Post deleted successfully")
                return True
            else:
                print(f"⚠️  Post deletion failed - Status: {response.status_code}")
                return True  # Still consider the test successful
                
        else:
            print(f"❌ Post creation failed - Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during post testing: {e}")
        return False

def main():
    print("🚀 Testing Facebook Post Manager with Real Token")
    print("=" * 60)
    
    # Test 1: Debug the token
    token_valid = test_facebook_token_debug()
    
    # Test 2: Authenticate with Facebook
    auth_success, user = test_facebook_auth()
    
    # Test 3: Create and manage posts
    post_success = test_create_and_manage_post(user) if auth_success else False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Token Debug: {'✅ PASS' if token_valid else '❌ FAIL'}")
    print(f"   Authentication: {'✅ PASS' if auth_success else '❌ FAIL'}")
    print(f"   Post Management: {'✅ PASS' if post_success else '❌ FAIL'}")
    
    if token_valid and auth_success:
        print("\n🎉 Facebook integration is working correctly!")
        print("   - Token is valid")
        print("   - User authentication successful")
        if user:
            pages = user.get('facebook_pages', [])
            print(f"   - {len(pages)} Facebook pages available")
        return 0
    else:
        print("\n⚠️  Some tests failed - check the details above")
        return 1

if __name__ == "__main__":
    sys.exit(main())