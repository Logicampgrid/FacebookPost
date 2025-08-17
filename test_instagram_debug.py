#!/usr/bin/env python3
"""
Debug script to test Instagram publication issues
"""

import requests
import json

API_BASE = "http://localhost:8001"

def test_instagram_permissions():
    """Test Instagram permissions and account access"""
    print("🔍 Testing Instagram account access and permissions...")
    
    try:
        # Test if we can find users with Instagram access
        response = requests.get(f"{API_BASE}/api/debug/store-platforms/gizmobbs")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'error' in data:
                print(f"❌ Store platforms error: {data['error']}")
                if 'No user' in data['error']:
                    print("💡 ISSUE IDENTIFIED: No authenticated Facebook user found!")
                    print("🔧 SOLUTION: Need to connect with Facebook Business Manager first")
                    return False
            
            instagram_accounts = data.get('platforms', {}).get('instagram_accounts', [])
            print(f"📸 Instagram accounts found: {len(instagram_accounts)}")
            
            if len(instagram_accounts) == 0:
                print("❌ NO INSTAGRAM ACCOUNTS FOUND!")
                print("💡 Possible issues:")
                print("  1. Instagram account not connected to Facebook Business page")
                print("  2. Instagram Business account required (not personal)")
                print("  3. Permissions missing for Instagram publishing")
                print("  4. Business Manager doesn't have access to Instagram account")
                return False
            
            for ig in instagram_accounts:
                print(f"✅ Instagram account: @{ig.get('username', 'unknown')} (ID: {ig.get('id', 'unknown')})")
                
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Test error: {e}")
        return False

def test_facebook_permissions():
    """Test Facebook permissions for posting"""
    print("\n🔍 Testing Facebook posting permissions...")
    
    try:
        response = requests.get(f"{API_BASE}/api/debug/pages")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'error' in data:
                print(f"❌ Pages debug error: {data['error']}")
                return False
                
            # Check personal and business manager pages
            personal_pages = data.get('personal_pages', [])
            business_pages = data.get('business_manager_pages', [])
            
            print(f"📘 Personal Facebook pages: {len(personal_pages)}")
            print(f"🏢 Business Manager pages: {len(business_pages)}")
            
            # Look for gizmobbs page
            gizmobbs_page = None
            for page in personal_pages + [page for bm in business_pages for page in bm.get('pages', [])]:
                if page.get('id') == '102401876209415' or 'berger' in page.get('name', '').lower():
                    gizmobbs_page = page
                    print(f"✅ Found gizmobbs page: {page.get('name')} (ID: {page.get('id')})")
                    break
            
            if not gizmobbs_page:
                print("❌ Gizmobbs Facebook page (Le Berger Blanc Suisse) NOT FOUND!")
                print("💡 Expected page ID: 102401876209415")
                return False
                
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Test error: {e}")
        return False

def test_instagram_connection_requirements():
    """Test what's needed for Instagram connection"""
    print("\n📋 Instagram Connection Requirements Checklist:")
    
    requirements = [
        "✅ Instagram Business Account (not personal)",
        "✅ Instagram account connected to Facebook Business Page",
        "✅ Facebook Business Manager access to Instagram account",
        "✅ 'instagram_basic' and 'instagram_content_publish' permissions",
        "✅ Valid Facebook access token with Instagram permissions",
        "✅ Page access token (not user token) for Instagram API calls"
    ]
    
    for req in requirements:
        print(f"  {req}")
    
    print("\n🔧 Common Instagram Publishing Issues:")
    issues = [
        "❌ Instagram account is Personal (needs to be Business/Creator)",
        "❌ Instagram not connected to Facebook Business page",
        "❌ Missing instagram_content_publish permission",
        "❌ Using user token instead of page token",
        "❌ Instagram account not accessible via Business Manager",
        "❌ Rate limiting on Instagram API (too many requests)"
    ]
    
    for issue in issues:
        print(f"  {issue}")
    
    return True

def test_multipart_webhook_debug():
    """Test webhook with debug info"""
    print("\n🔍 Testing webhook with debug information...")
    
    try:
        response = requests.get(f"{API_BASE}/api/webhook")
        
        if response.status_code == 200:
            data = response.json()
            shop_mapping = data.get('shop_mapping', {})
            gizmobbs_config = shop_mapping.get('gizmobbs', {})
            
            print(f"🐕 Gizmobbs configuration:")
            for key, value in gizmobbs_config.items():
                print(f"  {key}: {value}")
            
            if gizmobbs_config.get('platform') == 'multi':
                print("✅ Multi-platform configuration CONFIRMED")
                platforms = gizmobbs_config.get('platforms', [])
                print(f"📱 Target platforms: {platforms}")
                
                if 'instagram' in platforms and 'facebook' in platforms:
                    print("✅ Both Facebook and Instagram configured")
                    return True
                else:
                    print(f"❌ Missing platforms: expected ['facebook', 'instagram'], got {platforms}")
                    return False
            else:
                print(f"❌ Not configured for multi-platform: {gizmobbs_config.get('platform')}")
                return False
                
        else:
            print(f"❌ Webhook error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Test error: {e}")
        return False

def main():
    """Run Instagram debugging tests"""
    print("🎯 Instagram Publication Debug Analysis")
    print("=" * 60)
    
    tests = [
        ("Facebook Permissions", test_facebook_permissions),
        ("Instagram Account Access", test_instagram_permissions),
        ("Multi-platform Configuration", test_multipart_webhook_debug),
        ("Instagram Requirements", test_instagram_connection_requirements)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📊 INSTAGRAM DEBUG SUMMARY")
    print("=" * 60)
    
    issues_found = []
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ ISSUE"
        print(f"{status} {test_name}")
        if not passed:
            issues_found.append(test_name)
    
    if issues_found:
        print(f"\n🚨 ISSUES IDENTIFIED: {len(issues_found)}")
        print("\n💡 LIKELY ROOT CAUSE:")
        if "Instagram Account Access" in issues_found:
            print("  → Instagram account not properly connected to Business Manager")
            print("  → Need to link Instagram Business account to Facebook page")
        if "Facebook Permissions" in issues_found:
            print("  → Missing Facebook authentication or page access")
            print("  → Need to authenticate with Facebook Business Manager first")
            
        print("\n🔧 RECOMMENDED ACTIONS:")
        print("  1. Login to Facebook Business Manager")
        print("  2. Connect Instagram Business account to 'Le Berger Blanc Suisse' page")
        print("  3. Ensure Instagram account @logicamp_berger is accessible")
        print("  4. Re-authenticate in the web application")
    else:
        print("\n🎉 No major issues found - Instagram should work!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()