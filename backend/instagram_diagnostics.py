#!/usr/bin/env python3
"""
Instagram Publication Diagnostics - Advanced debugging tools
"""

import requests
import json
import os
from datetime import datetime

FACEBOOK_GRAPH_URL = "https://graph.facebook.com/v18.0"

class InstagramDiagnostics:
    def __init__(self, access_token=None):
        self.access_token = access_token
        
    def check_instagram_permissions(self, page_id):
        """Check if a Facebook page has Instagram permissions"""
        try:
            print(f"🔍 Checking Instagram permissions for page {page_id}")
            
            response = requests.get(
                f"{FACEBOOK_GRAPH_URL}/{page_id}",
                params={
                    "access_token": self.access_token,
                    "fields": "instagram_business_account,name,category"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                page_name = data.get("name", "Unknown")
                
                if "instagram_business_account" in data:
                    ig_id = data["instagram_business_account"]["id"]
                    print(f"✅ Page '{page_name}' has Instagram Business account: {ig_id}")
                    return ig_id
                else:
                    print(f"❌ Page '{page_name}' has NO Instagram Business account connected")
                    return None
            else:
                error = response.json()
                print(f"❌ Error checking page: {error}")
                return None
                
        except Exception as e:
            print(f"💥 Exception checking Instagram permissions: {e}")
            return None
    
    def check_instagram_account_info(self, instagram_id):
        """Get detailed Instagram account information"""
        try:
            print(f"📱 Getting Instagram account info for {instagram_id}")
            
            response = requests.get(
                f"{FACEBOOK_GRAPH_URL}/{instagram_id}",
                params={
                    "access_token": self.access_token,
                    "fields": "id,username,name,account_type,media_count,followers_count"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Instagram Account Details:")
                print(f"   📱 Username: @{data.get('username', 'N/A')}")
                print(f"   📝 Name: {data.get('name', 'N/A')}")
                print(f"   🏢 Type: {data.get('account_type', 'N/A')}")
                print(f"   📊 Media: {data.get('media_count', 0)} posts")
                print(f"   👥 Followers: {data.get('followers_count', 0)}")
                return data
            else:
                error = response.json()
                print(f"❌ Error getting Instagram info: {error}")
                return None
                
        except Exception as e:
            print(f"💥 Exception getting Instagram info: {e}")
            return None
    
    def test_instagram_posting_permissions(self, instagram_id):
        """Test if we can create Instagram media containers"""
        try:
            print(f"🧪 Testing Instagram posting permissions for {instagram_id}")
            
            # Try to create a dummy media container (won't publish)
            test_data = {
                "access_token": self.access_token,
                "caption": "Test caption for permission check",
                "image_url": "https://picsum.photos/800/800?test=" + str(datetime.now().timestamp())
            }
            
            response = requests.post(
                f"{FACEBOOK_GRAPH_URL}/{instagram_id}/media",
                data=test_data
            )
            
            if response.status_code == 200:
                result = response.json()
                container_id = result.get("id")
                print(f"✅ Instagram posting permissions OK - test container created: {container_id}")
                
                # Clean up - delete the test container (don't publish)
                try:
                    delete_response = requests.delete(
                        f"{FACEBOOK_GRAPH_URL}/{container_id}",
                        params={"access_token": self.access_token}
                    )
                    print(f"🧹 Test container cleaned up")
                except:
                    print(f"⚠️ Could not clean up test container (not critical)")
                
                return True
            else:
                error = response.json()
                print(f"❌ Instagram posting permissions FAILED: {error}")
                
                # Analyze specific error codes
                if error.get("error", {}).get("code") == 100:
                    print("🔍 Error 100: Invalid parameter or permission issue")
                elif error.get("error", {}).get("code") == 200:
                    print("🔍 Error 200: Permission denied for this Instagram account")
                elif "does not exist" in str(error):
                    print("🔍 Instagram account may not exist or not be accessible")
                
                return False
                
        except Exception as e:
            print(f"💥 Exception testing Instagram permissions: {e}")
            return False
    
    def diagnose_instagram_issue(self, page_id):
        """Complete diagnosis of Instagram connectivity"""
        print(f"\n🎯 COMPLETE INSTAGRAM DIAGNOSIS FOR PAGE {page_id}")
        print("=" * 60)
        
        issues = []
        
        # Step 1: Check if page has Instagram connected
        instagram_id = self.check_instagram_permissions(page_id)
        if not instagram_id:
            issues.append("No Instagram Business account connected to Facebook page")
            return issues
        
        # Step 2: Get Instagram account details
        ig_info = self.check_instagram_account_info(instagram_id)
        if not ig_info:
            issues.append("Cannot access Instagram account details")
            return issues
        
        # Step 3: Test posting permissions
        can_post = self.test_instagram_posting_permissions(instagram_id)
        if not can_post:
            issues.append("No Instagram posting permissions")
        
        # Step 4: Additional checks
        if ig_info.get("account_type") != "BUSINESS":
            issues.append(f"Instagram account type is '{ig_info.get('account_type')}' - should be BUSINESS")
        
        print(f"\n📋 DIAGNOSIS COMPLETE")
        if issues:
            print(f"❌ {len(issues)} issues found:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print(f"✅ Instagram setup looks good for @{ig_info.get('username')}")
        
        return issues
    
    def get_business_manager_instagram_accounts(self, business_manager_id):
        """Get all Instagram accounts from Business Manager"""
        try:
            print(f"🏢 Getting Instagram accounts from Business Manager {business_manager_id}")
            
            # Get pages from Business Manager
            response = requests.get(
                f"{FACEBOOK_GRAPH_URL}/{business_manager_id}/client_pages",
                params={
                    "access_token": self.access_token,
                    "fields": "id,name,instagram_business_account"
                }
            )
            
            if response.status_code == 200:
                pages = response.json().get("data", [])
                instagram_accounts = []
                
                for page in pages:
                    if "instagram_business_account" in page:
                        ig_id = page["instagram_business_account"]["id"]
                        ig_info = self.check_instagram_account_info(ig_id)
                        if ig_info:
                            ig_info["connected_page_name"] = page["name"]
                            ig_info["connected_page_id"] = page["id"]
                            instagram_accounts.append(ig_info)
                
                print(f"✅ Found {len(instagram_accounts)} Instagram accounts in Business Manager")
                return instagram_accounts
            else:
                error = response.json()
                print(f"❌ Error getting Business Manager pages: {error}")
                return []
                
        except Exception as e:
            print(f"💥 Exception getting BM Instagram accounts: {e}")
            return []

def run_complete_diagnosis(access_token=None):
    """Run complete Instagram diagnosis"""
    print("🎯 INSTAGRAM PUBLICATION DIAGNOSTIC TOOL")
    print("=" * 60)
    
    if not access_token:
        print("❌ No access token provided")
        print("💡 Need Facebook page access token to run diagnosis")
        return
    
    diagnostics = InstagramDiagnostics(access_token)
    
    # Test with known page ID from config
    test_page_id = "102401876209415"  # Le Berger Blanc Suisse
    
    print(f"🧪 Testing with page ID: {test_page_id}")
    issues = diagnostics.diagnose_instagram_issue(test_page_id)
    
    print(f"\n🎯 NEXT STEPS:")
    if issues:
        print("1. 🔧 Fix the identified issues")
        print("2. 🔑 Ensure proper Facebook Business Manager setup")
        print("3. 📱 Connect Instagram Business account to Facebook page")
        print("4. ✅ Test again after fixes")
    else:
        print("1. ✅ Instagram setup is correct!")
        print("2. 🚀 Try publishing a test post")
        print("3. 📊 Monitor posting results")

if __name__ == "__main__":
    print("⚠️ This script requires a valid Facebook page access token")
    print("Run from the main application with proper authentication")