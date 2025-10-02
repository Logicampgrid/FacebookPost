#!/usr/bin/env python3
"""
Review Request Specific Backend Testing
Testing the specific endpoints mentioned in the review request
"""

import requests
import sys
import json
from datetime import datetime

class ReviewRequestTester:
    def __init__(self, base_url="https://media-post.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)[:300]}...")
                except:
                    print(f"   Error: {response.text[:300]}...")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_instagram_permissions_guide(self):
        """Test Instagram permissions guide endpoint (REVIEW REQUEST #1)"""
        success, response = self.run_test(
            "Instagram Permissions Guide",
            "GET",
            "api/instagram-permissions-guide",
            200
        )
        
        if success:
            status = response.get("status", "")
            problem_analysis = response.get("problem_analysis", {})
            solution_steps = response.get("solution_steps", [])
            temporary_solution = response.get("temporary_solution", {})
            
            print(f"   Status: {status}")
            print(f"   Missing permissions: {problem_analysis.get('missing_permissions', [])}")
            print(f"   Solution steps: {len(solution_steps)}")
            print(f"   Business Manager access: {problem_analysis.get('business_manager_access', 'Unknown')}")
            print(f"   Instagram account: {problem_analysis.get('instagram_account', 'Unknown')}")
            
            # Check if guide mentions @logicamp_berger
            response_str = str(response)
            if "logicamp_berger" in response_str:
                print("✅ Guide mentions @logicamp_berger account")
            else:
                print("⚠️  Guide doesn't mention @logicamp_berger account")
                
            # Check for required fields
            required_fields = ["status", "problem_analysis", "solution_steps", "temporary_solution"]
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                print("✅ All required fields present")
            else:
                print(f"❌ Missing fields: {missing_fields}")
        
        return success

    def test_business_manager_access_debug(self):
        """Test Business Manager access debug endpoint (REVIEW REQUEST #2)"""
        success, response = self.run_test(
            "Business Manager Access Debug",
            "GET",
            "api/debug/business-manager-access",
            200
        )
        
        if success:
            if "error" in response:
                # No authenticated user case
                error = response.get("error", "")
                solution = response.get("solution", "")
                print(f"   Error: {error}")
                print(f"   Solution: {solution}")
                
                if "No authenticated user found" in error:
                    print("✅ Expected: No authenticated user found")
                else:
                    print("⚠️  Unexpected error message")
            else:
                # User found case
                user_name = response.get("user_name", "")
                business_managers = response.get("current_business_managers", [])
                instagram_analysis = response.get("instagram_access_analysis", {})
                
                print(f"   User: {user_name}")
                print(f"   Business Managers: {len(business_managers)}")
                print(f"   Instagram access status: {instagram_analysis.get('access_status', 'Unknown')}")
                print(f"   Can publish Instagram: {instagram_analysis.get('can_publish_instagram', False)}")
                
                # Check for Didier Preud'homme Business Manager
                didier_bm_found = any("didier" in bm.get("name", "").lower() or "preud'homme" in bm.get("name", "").lower() 
                                    for bm in business_managers)
                if didier_bm_found:
                    print("✅ Found 'Entreprise de Didier Preud'homme' Business Manager")
                else:
                    print("⚠️  'Entreprise de Didier Preud'homme' Business Manager not found")
        
        return success

    def test_logicamp_berger_final_test(self):
        """Test @logicamp_berger final publication test (REVIEW REQUEST #3)"""
        success, response = self.run_test(
            "Logicamp Berger Final Test",
            "POST",
            "api/debug/test-logicamp-berger-final",
            200
        )
        
        if success:
            test_success = response.get("success", False)
            message = response.get("message", "")
            configuration_status = response.get("configuration_status", "")
            results = response.get("results", {})
            webhook_ready = response.get("webhook_ready", {})
            
            print(f"   Success: {test_success}")
            print(f"   Message: {message}")
            print(f"   Configuration: {configuration_status}")
            
            if test_success:
                # Success case - Facebook publication worked
                facebook_result = results.get("facebook", {})
                instagram_result = results.get("instagram", {})
                
                print(f"   Facebook status: {facebook_result.get('status', 'Unknown')}")
                print(f"   Facebook post ID: {facebook_result.get('post_id', 'None')}")
                print(f"   Instagram status: {instagram_result.get('status', 'Unknown')}")
                
                if facebook_result.get("status") == "✅ SUCCESS":
                    print("✅ Facebook publication successful")
                else:
                    print("⚠️  Facebook publication status unclear")
                    
                if "PENDING" in instagram_result.get("status", ""):
                    print("✅ Instagram correctly shows pending permissions")
                else:
                    print("⚠️  Instagram status unclear")
                    
                # Check webhook readiness for gizmobbs
                gizmobbs_status = webhook_ready.get("gizmobbs", "")
                if "Opérationnel" in gizmobbs_status:
                    print("✅ Gizmobbs webhook ready for Facebook")
                else:
                    print("⚠️  Gizmobbs webhook status unclear")
                    
            else:
                # Error case - expected if no user authenticated
                error = response.get("error", "")
                print(f"   Error: {error}")
                
                if "Aucun utilisateur authentifié" in error:
                    print("✅ Expected: No authenticated user")
                elif "Business Manager" in error:
                    print("✅ Expected: Business Manager access issue")
                else:
                    print("⚠️  Unexpected error type")
        
        return success

    def test_health_check(self):
        """Test health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        
        if success:
            status = response.get("status", "")
            backend = response.get("backend", "")
            mongodb = response.get("mongodb", "")
            database = response.get("database", {})
            
            print(f"   Status: {status}")
            print(f"   Backend: {backend}")
            print(f"   MongoDB: {mongodb}")
            print(f"   Users: {database.get('users_count', 0)}")
            print(f"   Posts: {database.get('posts_count', 0)}")
            
            if status == "healthy" and backend == "running":
                print("✅ Backend is healthy and running")
            else:
                print("⚠️  Backend status unclear")
        
        return success

    def run_review_tests(self):
        """Run all review request specific tests"""
        print("🎯 REVIEW REQUEST BACKEND TESTING")
        print("=" * 50)
        print(f"🌐 Testing against: {self.base_url}")
        print(f"📅 Test time: {datetime.utcnow().isoformat()}")
        print()
        
        # Run the specific tests mentioned in the review request
        tests = [
            ("Health Check", self.test_health_check),
            ("Instagram Permissions Guide", self.test_instagram_permissions_guide),
            ("Business Manager Access", self.test_business_manager_access_debug),
            ("Logicamp Berger Final Test", self.test_logicamp_berger_final_test),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                results[test_name] = result
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                results[test_name] = False
        
        # Summary
        print("\n" + "="*60)
        print("📊 REVIEW REQUEST TEST SUMMARY")
        print("="*60)
        
        passed = sum(results.values())
        total = len(results)
        
        print(f"Total tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success rate: {(passed/total)*100:.1f}%")
        
        print("\n🎯 INDIVIDUAL TEST RESULTS:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {test_name}")
        
        # Overall assessment
        if passed == total:
            print(f"\n🏆 ALL REVIEW REQUEST TESTS PASSED!")
            print("✅ Instagram permissions guide is working")
            print("✅ Business Manager access debug is working")
            print("✅ Logicamp Berger final test is working")
            print("✅ Backend is healthy and responsive")
        elif passed >= 3:
            print(f"\n✅ MOST REVIEW REQUEST TESTS PASSED ({passed}/{total})")
            print("⚠️  Minor issues detected - see individual test results")
        else:
            print(f"\n❌ MULTIPLE REVIEW REQUEST TESTS FAILED ({total-passed}/{total})")
            print("🔧 Backend requires attention before frontend testing")
        
        return passed == total

def main():
    """Main test execution"""
    tester = ReviewRequestTester()
    success = tester.run_review_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())