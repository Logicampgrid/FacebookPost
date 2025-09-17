#!/usr/bin/env python3
"""
Backend API Testing for FacebookPost Application - Instagram Diagnostics Fix
Testing the corrections for: "can't access property 'user_found', a.authentication is undefined"
"""

import requests
import json
import sys
from datetime import datetime

class InstagramDiagnosticsAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []

    def log(self, message, level="INFO"):
        """Log test messages"""
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
        icon = icons.get(level.upper(), "📋")
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{icon} [{timestamp}] {message}")

    def run_test(self, name, method, endpoint, expected_status=200, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        self.log(f"Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}", "SUCCESS")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, response.text
            else:
                error_msg = f"❌ {name} - Expected {expected_status}, got {response.status_code}"
                self.log(error_msg, "ERROR")
                self.errors.append(f"{name}: {error_msg}")
                try:
                    error_data = response.json()
                    self.log(f"Response: {json.dumps(error_data, indent=2)}", "ERROR")
                    return False, error_data
                except:
                    self.log(f"Response: {response.text}", "ERROR")
                    return False, response.text

        except requests.exceptions.ConnectionError:
            error_msg = f"❌ {name} - Connection refused. Is the backend running?"
            self.log(error_msg, "ERROR")
            self.errors.append(f"{name}: Connection refused")
            return False, {"error": "Connection refused"}
        except Exception as e:
            error_msg = f"❌ {name} - Error: {str(e)}"
            self.log(error_msg, "ERROR")
            self.errors.append(f"{name}: {str(e)}")
            return False, {"error": str(e)}

    def test_health_check(self):
        """Test the health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "/api/health",
            200
        )
        
        if success and isinstance(response, dict):
            if "status" in response and response["status"] == "healthy":
                self.log("✅ Backend is healthy and running", "SUCCESS")
                return True
            else:
                self.log(f"Unexpected health response: {response}", "WARNING")
                return False
        return success

    def test_instagram_diagnosis_critical_fix(self):
        """Test Instagram complete diagnosis endpoint - CRITICAL TEST FOR THE FIX"""
        self.log("🔍 Testing Instagram diagnosis (CRITICAL FIX)...", "INFO")
        self.log("Focus: Ensuring 'authentication.user_found' is accessible", "INFO")
        
        success, response = self.run_test(
            "Instagram Complete Diagnosis",
            "GET",
            "/api/debug/instagram-complete-diagnosis",
            200
        )
        
        if not success:
            self.log("❌ CRITICAL: Instagram diagnosis endpoint failed", "ERROR")
            return False
        
        if not isinstance(response, dict):
            self.log("❌ CRITICAL: Response is not a JSON object", "ERROR")
            return False
        
        # CRITICAL CHECK 1: Authentication object exists
        if "authentication" not in response:
            self.log("❌ CRITICAL: Missing 'authentication' in response", "ERROR")
            self.errors.append("Instagram Diagnosis: Missing authentication object")
            return False
        
        auth = response["authentication"]
        
        # CRITICAL CHECK 2: Authentication is not None/undefined
        if auth is None:
            self.log("❌ CRITICAL: authentication is null/None", "ERROR")
            self.errors.append("Instagram Diagnosis: authentication is null")
            return False
        
        # CRITICAL CHECK 3: Authentication is an object (dict)
        if not isinstance(auth, dict):
            self.log(f"❌ CRITICAL: authentication is not an object, it's {type(auth)}", "ERROR")
            self.errors.append(f"Instagram Diagnosis: authentication is {type(auth)}, not dict")
            return False
        
        # CRITICAL CHECK 4: user_found property exists
        if "user_found" not in auth:
            self.log("❌ CRITICAL: authentication object missing 'user_found' property", "ERROR")
            self.errors.append("Instagram Diagnosis: Missing user_found property")
            return False
        
        # SUCCESS - The fix is working!
        self.log("✅ FIXED: authentication.user_found is accessible!", "SUCCESS")
        self.log(f"✅ User found: {auth['user_found']}", "SUCCESS")
        
        # Additional verification
        if auth.get("user_name"):
            self.log(f"✅ User name: {auth['user_name']}", "SUCCESS")
        if auth.get("user_id"):
            self.log(f"✅ User ID: {auth['user_id']}", "SUCCESS")
        
        business_managers_count = auth.get("business_managers_count", 0)
        self.log(f"✅ Business Managers: {business_managers_count}", "SUCCESS")
        
        # Check Instagram accounts
        ig_accounts = response.get("instagram_accounts", [])
        self.log(f"✅ Instagram accounts found: {len(ig_accounts)}", "SUCCESS")
        
        # Look for @logicamp_berger specifically
        logicamp_found = False
        for account in ig_accounts:
            username = account.get("username", "")
            if username == "logicamp_berger":
                logicamp_found = True
                self.log("✅ Found @logicamp_berger account!", "SUCCESS")
                break
        
        if not logicamp_found and len(ig_accounts) > 0:
            self.log("⚠️ @logicamp_berger not found, but other accounts exist:", "WARNING")
            for account in ig_accounts:
                self.log(f"  - @{account.get('username', 'unknown')}", "INFO")
        elif len(ig_accounts) == 0:
            self.log("⚠️ No Instagram accounts found", "WARNING")
        
        # Verify expected data structure matches the review request
        expected_user = "Didier Preud'homme"
        expected_user_id = "10218839709543601"
        expected_bm_count = 4
        expected_ig_count = 8
        expected_fb_pages = 15
        
        if auth.get("user_name") == expected_user:
            self.log(f"✅ Expected user found: {expected_user}", "SUCCESS")
        
        if str(auth.get("user_id")) == expected_user_id:
            self.log(f"✅ Expected user ID found: {expected_user_id}", "SUCCESS")
        
        if business_managers_count == expected_bm_count:
            self.log(f"✅ Expected Business Managers count: {expected_bm_count}", "SUCCESS")
        
        if len(ig_accounts) == expected_ig_count:
            self.log(f"✅ Expected Instagram accounts count: {expected_ig_count}", "SUCCESS")
        
        fb_pages_count = response.get("facebook_pages_count", 0)
        if fb_pages_count == expected_fb_pages:
            self.log(f"✅ Expected Facebook pages count: {expected_fb_pages}", "SUCCESS")
        
        return True

    def test_facebook_auth_endpoint(self):
        """Test Facebook authentication endpoint"""
        self.log("Testing Facebook auth endpoint...", "INFO")
        
        test_data = {
            "access_token": "test_token_for_endpoint_validation"
        }
        
        success, response = self.run_test(
            "Facebook Authentication",
            "POST",
            "/api/auth/facebook",
            expected_status=200,
            data=test_data
        )
        
        # Even if authentication fails due to invalid token, 
        # the endpoint should respond properly (not crash)
        if not success and isinstance(response, dict):
            if "error" in response or "success" in response:
                self.log("✅ Endpoint responds properly with error handling", "SUCCESS")
                return True
        
        return success

    def test_facebook_exchange_code_endpoint(self):
        """Test Facebook code exchange endpoint"""
        self.log("Testing Facebook exchange code endpoint...", "INFO")
        
        test_data = {
            "code": "test_code_for_endpoint_validation",
            "state": "test_state",
            "store": "gizmobbs"
        }
        
        success, response = self.run_test(
            "Facebook Exchange Code",
            "POST",
            "/api/auth/facebook/exchange-code",
            expected_status=200,
            data=test_data
        )
        
        # Even if exchange fails due to invalid code,
        # the endpoint should respond properly (not crash)
        if not success and isinstance(response, dict):
            if "error" in response or "success" in response:
                self.log("✅ Endpoint responds properly with error handling", "SUCCESS")
                return True
        
        return success

    def run_all_tests(self):
        """Run all backend tests focused on the Instagram diagnostics fix"""
        self.log("🚀 Starting FacebookPost Backend API Tests", "INFO")
        self.log(f"📡 Testing against: {self.base_url}", "INFO")
        self.log("🎯 FOCUS: Instagram Diagnostics Fix - 'authentication.user_found' accessibility", "INFO")
        self.log("=" * 80, "INFO")
        
        # Priority 1: Health Check
        self.log("PRIORITY 1: Basic API Health", "INFO")
        health_ok = self.test_health_check()
        
        if not health_ok:
            self.log("❌ Health check failed - backend may not be running", "ERROR")
            self.log("🛑 Stopping tests - fix backend connectivity first", "ERROR")
            return False
        
        # Priority 2: Instagram Diagnosis (Critical Fix)
        self.log("\nPRIORITY 2: Instagram Diagnosis (CRITICAL FIX)", "INFO")
        diagnosis_ok = self.test_instagram_diagnosis_critical_fix()
        
        # Priority 3: Authentication Endpoints
        self.log("\nPRIORITY 3: Authentication Endpoints", "INFO")
        auth_ok = self.test_facebook_auth_endpoint()
        exchange_ok = self.test_facebook_exchange_code_endpoint()
        
        # Summary
        self.log("\n" + "=" * 80, "INFO")
        self.log(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed", "INFO")
        
        if self.errors:
            self.log("❌ FAILED TESTS:", "ERROR")
            for error in self.errors:
                self.log(f"  - {error}", "ERROR")
        
        # Critical assessment
        if diagnosis_ok:
            self.log("✅ CRITICAL FIX VERIFIED: Instagram diagnosis working!", "SUCCESS")
            self.log("✅ 'authentication.user_found' is now accessible", "SUCCESS")
            self.log("✅ JavaScript error should be resolved", "SUCCESS")
            
            if auth_ok or exchange_ok:
                self.log("✅ Authentication endpoints responding properly", "SUCCESS")
            
            return True
        else:
            self.log("❌ CRITICAL ISSUE: Instagram diagnosis still broken", "ERROR")
            self.log("❌ JavaScript error 'can't access property user_found' may persist", "ERROR")
            return False

def main():
    """Main test execution"""
    # Use the backend URL from frontend .env
    backend_url = "http://localhost:8001"
    
    print("🔧 FacebookPost Application - Instagram Diagnostics Fix Test")
    print(f"📡 Backend URL: {backend_url}")
    print("🎯 Testing fix for: 'can't access property 'user_found', a.authentication is undefined'")
    print("=" * 80)
    
    tester = InstagramDiagnosticsAPITester(backend_url)
    success = tester.run_all_tests()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ BACKEND TESTS PASSED - Ready for frontend testing")
    else:
        print("❌ BACKEND TESTS FAILED - Fix backend issues before frontend testing")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())