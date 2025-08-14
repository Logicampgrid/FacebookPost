import requests
import sys
import json
from datetime import datetime
import uuid

class N8NIntegrationTester:
    def __init__(self, base_url="https://ok-minimal.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user_created = False

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2, default=str)[:300]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_setup_test_user(self):
        """Test setting up test user for n8n integration"""
        success, response = self.run_test(
            "Setup Test User for N8N",
            "POST",
            "api/publishProduct/setup-test-user",
            200
        )
        
        if success:
            status = response.get("status")
            user_info = response.get("user", {})
            usage_info = response.get("usage", {})
            
            if status == "success":
                print(f"✅ Test user setup successful")
                print(f"   User ID: {user_info.get('facebook_id')}")
                print(f"   Pages: {len(user_info.get('pages', []))}")
                print(f"   Usage - User ID: {usage_info.get('user_id')}")
                print(f"   Usage - Page ID: {usage_info.get('page_id')}")
                self.test_user_created = True
            else:
                print(f"⚠️ Unexpected status: {status}")
        
        return success

    def test_get_config(self):
        """Test GET /api/publishProduct/config endpoint"""
        success, response = self.run_test(
            "Get PublishProduct Config",
            "GET",
            "api/publishProduct/config",
            200
        )
        
        if success:
            users = response.get("users", [])
            total_pages = response.get("total_pages", 0)
            
            print(f"   Found {len(users)} users")
            print(f"   Total pages: {total_pages}")
            
            if len(users) > 0:
                print("✅ Configuration endpoint returns users")
                # Check structure of first user
                first_user = users[0]
                required_fields = ["id", "name", "facebook_id"]
                for field in required_fields:
                    if field in first_user:
                        print(f"   ✅ User has {field}: {first_user[field]}")
                    else:
                        print(f"   ❌ User missing {field}")
            else:
                print("⚠️ No users found in configuration")
        
        return success

    def test_publish_product_valid(self):
        """Test POST /api/publishProduct with valid data"""
        product_data = {
            "title": "Canapé moderne test",
            "description": "Un canapé moderne très confortable, parfait pour le salon",
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
            "product_url": "https://example.com/canape-moderne",
            "user_id": "test_user_n8n",
            "page_id": "test_page_n8n_1"
        }
        
        success, response = self.run_test(
            "Publish Product (Valid Data)",
            "POST",
            "api/publishProduct",
            200,
            data=product_data
        )
        
        if success:
            status = response.get("status")
            message = response.get("message")
            data = response.get("data", {})
            
            if status == "success":
                print("✅ Product published successfully")
                print(f"   Message: {message}")
                print(f"   Facebook Post ID: {data.get('facebook_post_id')}")
                print(f"   Page Name: {data.get('page_name')}")
                print(f"   User Name: {data.get('user_name')}")
                print(f"   Comment Added: {data.get('comment_added')}")
                print(f"   Published At: {data.get('published_at')}")
                
                # Validate required response fields
                required_fields = ["facebook_post_id", "post_id", "page_name", "page_id"]
                for field in required_fields:
                    if field in data:
                        print(f"   ✅ Response has {field}")
                    else:
                        print(f"   ❌ Response missing {field}")
            else:
                print(f"⚠️ Unexpected status: {status}")
        
        return success

    def test_publish_product_test_endpoint(self):
        """Test POST /api/publishProduct/test endpoint"""
        product_data = {
            "title": "Canapé moderne test",
            "description": "Un canapé moderne très confortable, parfait pour le salon",
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
            "product_url": "https://example.com/canape-moderne",
            "user_id": "test_user_n8n",
            "page_id": "test_page_n8n_1"
        }
        
        success, response = self.run_test(
            "Publish Product Test Endpoint",
            "POST",
            "api/publishProduct/test",
            200,
            data=product_data
        )
        
        if success:
            status = response.get("status")
            if status == "success":
                print("✅ Test endpoint working correctly")
            else:
                print(f"⚠️ Unexpected test status: {status}")
        
        return success

    def test_publish_product_missing_title(self):
        """Test validation: missing title"""
        product_data = {
            "description": "Un canapé moderne très confortable",
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
            "product_url": "https://example.com/canape-moderne",
            "user_id": "test_user_n8n",
            "page_id": "test_page_n8n_1"
        }
        
        success, response = self.run_test(
            "Publish Product (Missing Title)",
            "POST",
            "api/publishProduct",
            400,
            data=product_data
        )
        
        if success:
            detail = response.get("detail")
            if "title" in str(detail).lower():
                print("✅ Correct validation error for missing title")
            else:
                print(f"⚠️ Unexpected error message: {detail}")
        
        return success

    def test_publish_product_empty_title(self):
        """Test validation: empty title"""
        product_data = {
            "title": "",
            "description": "Un canapé moderne très confortable",
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
            "product_url": "https://example.com/canape-moderne",
            "user_id": "test_user_n8n",
            "page_id": "test_page_n8n_1"
        }
        
        success, response = self.run_test(
            "Publish Product (Empty Title)",
            "POST",
            "api/publishProduct",
            400,
            data=product_data
        )
        
        if success:
            detail = response.get("detail")
            if "title" in str(detail).lower():
                print("✅ Correct validation error for empty title")
            else:
                print(f"⚠️ Unexpected error message: {detail}")
        
        return success

    def test_publish_product_missing_description(self):
        """Test validation: missing description"""
        product_data = {
            "title": "Canapé moderne test",
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
            "product_url": "https://example.com/canape-moderne",
            "user_id": "test_user_n8n",
            "page_id": "test_page_n8n_1"
        }
        
        success, response = self.run_test(
            "Publish Product (Missing Description)",
            "POST",
            "api/publishProduct",
            400,
            data=product_data
        )
        
        if success:
            detail = response.get("detail")
            if "description" in str(detail).lower():
                print("✅ Correct validation error for missing description")
            else:
                print(f"⚠️ Unexpected error message: {detail}")
        
        return success

    def test_publish_product_invalid_image_url(self):
        """Test validation: invalid image URL"""
        product_data = {
            "title": "Canapé moderne test",
            "description": "Un canapé moderne très confortable",
            "image_url": "not-a-valid-url",
            "product_url": "https://example.com/canape-moderne",
            "user_id": "test_user_n8n",
            "page_id": "test_page_n8n_1"
        }
        
        success, response = self.run_test(
            "Publish Product (Invalid Image URL)",
            "POST",
            "api/publishProduct",
            400,
            data=product_data
        )
        
        if success:
            detail = response.get("detail")
            if "image" in str(detail).lower() or "url" in str(detail).lower():
                print("✅ Correct validation error for invalid image URL")
            else:
                print(f"⚠️ Unexpected error message: {detail}")
        
        return success

    def test_publish_product_invalid_product_url(self):
        """Test validation: invalid product URL"""
        product_data = {
            "title": "Canapé moderne test",
            "description": "Un canapé moderne très confortable",
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
            "product_url": "not-a-valid-url",
            "user_id": "test_user_n8n",
            "page_id": "test_page_n8n_1"
        }
        
        success, response = self.run_test(
            "Publish Product (Invalid Product URL)",
            "POST",
            "api/publishProduct",
            400,
            data=product_data
        )
        
        if success:
            detail = response.get("detail")
            if "product" in str(detail).lower() or "url" in str(detail).lower():
                print("✅ Correct validation error for invalid product URL")
            else:
                print(f"⚠️ Unexpected error message: {detail}")
        
        return success

    def test_publish_product_with_api_key(self):
        """Test publishing with API key"""
        product_data = {
            "title": "Canapé moderne avec API key",
            "description": "Un canapé moderne très confortable, testé avec API key",
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
            "product_url": "https://example.com/canape-moderne-api",
            "user_id": "test_user_n8n",
            "page_id": "test_page_n8n_1",
            "api_key": "test_api_key_12345"
        }
        
        success, response = self.run_test(
            "Publish Product (With API Key)",
            "POST",
            "api/publishProduct",
            200,
            data=product_data
        )
        
        if success:
            status = response.get("status")
            if status == "success":
                print("✅ Product published successfully with API key")
            else:
                print(f"⚠️ Unexpected status with API key: {status}")
        
        return success

    def test_publish_product_without_user_page_ids(self):
        """Test publishing without specifying user_id and page_id (should use defaults)"""
        product_data = {
            "title": "Canapé moderne sans IDs",
            "description": "Un canapé moderne très confortable, sans spécifier user_id et page_id",
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
            "product_url": "https://example.com/canape-moderne-default"
        }
        
        success, response = self.run_test(
            "Publish Product (No User/Page IDs)",
            "POST",
            "api/publishProduct",
            200,
            data=product_data
        )
        
        if success:
            status = response.get("status")
            data = response.get("data", {})
            if status == "success":
                print("✅ Product published successfully with default user/page")
                print(f"   Used Page: {data.get('page_name')}")
                print(f"   Used User: {data.get('user_name')}")
            else:
                print(f"⚠️ Unexpected status without IDs: {status}")
        
        return success

    def test_publish_product_nonexistent_user(self):
        """Test publishing with non-existent user_id"""
        product_data = {
            "title": "Canapé moderne utilisateur inexistant",
            "description": "Un canapé moderne très confortable",
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
            "product_url": "https://example.com/canape-moderne",
            "user_id": "nonexistent_user_12345",
            "page_id": "test_page_n8n_1"
        }
        
        success, response = self.run_test(
            "Publish Product (Nonexistent User)",
            "POST",
            "api/publishProduct",
            500,  # Should fail with internal server error
            data=product_data
        )
        
        if success:
            detail = response.get("detail")
            if isinstance(detail, dict):
                error_type = detail.get("error_type")
                if error_type == "authentication_error":
                    print("✅ Correct error type for nonexistent user")
                else:
                    print(f"⚠️ Unexpected error type: {error_type}")
            else:
                print(f"   Error detail: {detail}")
        
        return success

    def test_publish_product_nonexistent_page(self):
        """Test publishing with non-existent page_id"""
        product_data = {
            "title": "Canapé moderne page inexistante",
            "description": "Un canapé moderne très confortable",
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
            "product_url": "https://example.com/canape-moderne",
            "user_id": "test_user_n8n",
            "page_id": "nonexistent_page_12345"
        }
        
        success, response = self.run_test(
            "Publish Product (Nonexistent Page)",
            "POST",
            "api/publishProduct",
            200,  # Should succeed but use default page
            data=product_data
        )
        
        if success:
            status = response.get("status")
            data = response.get("data", {})
            if status == "success":
                print("✅ Used default page when specified page not found")
                print(f"   Used Page: {data.get('page_name')} (ID: {data.get('page_id')})")
            else:
                print(f"⚠️ Unexpected status for nonexistent page: {status}")
        
        return success

    def test_publish_product_unreachable_image(self):
        """Test publishing with unreachable image URL"""
        product_data = {
            "title": "Canapé moderne image inaccessible",
            "description": "Un canapé moderne très confortable",
            "image_url": "https://this-domain-definitely-does-not-exist-12345.com/image.jpg",
            "product_url": "https://example.com/canape-moderne",
            "user_id": "test_user_n8n",
            "page_id": "test_page_n8n_1"
        }
        
        success, response = self.run_test(
            "Publish Product (Unreachable Image)",
            "POST",
            "api/publishProduct",
            500,  # Should fail with image download error
            data=product_data
        )
        
        if success:
            detail = response.get("detail")
            if isinstance(detail, dict):
                error_type = detail.get("error_type")
                if error_type == "image_download_error":
                    print("✅ Correct error type for unreachable image")
                else:
                    print(f"⚠️ Unexpected error type: {error_type}")
            else:
                print(f"   Error detail: {detail}")
        
        return success

    def test_cleanup_test_user(self):
        """Test DELETE /api/publishProduct/cleanup-test-user endpoint"""
        success, response = self.run_test(
            "Cleanup Test User",
            "DELETE",
            "api/publishProduct/cleanup-test-user",
            200
        )
        
        if success:
            status = response.get("status")
            deleted = response.get("deleted", {})
            
            if status == "success":
                print("✅ Test data cleanup successful")
                print(f"   Deleted users: {deleted.get('users', 0)}")
                print(f"   Deleted posts: {deleted.get('posts', 0)}")
            else:
                print(f"⚠️ Unexpected cleanup status: {status}")
        
        return success

    def test_response_format_consistency(self):
        """Test that all endpoints return consistent response formats"""
        print(f"\n🔍 Testing Response Format Consistency...")
        
        # Test successful response format
        product_data = {
            "title": "Test format consistency",
            "description": "Testing response format",
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
            "product_url": "https://example.com/test-format",
            "user_id": "test_user_n8n",
            "page_id": "test_page_n8n_1"
        }
        
        success, response = self.run_test(
            "Response Format (Success)",
            "POST",
            "api/publishProduct",
            200,
            data=product_data
        )
        
        if success:
            # Check required fields in success response
            required_fields = ["status", "message", "data"]
            for field in required_fields:
                if field in response:
                    print(f"   ✅ Success response has {field}")
                else:
                    print(f"   ❌ Success response missing {field}")
            
            # Check data structure
            data = response.get("data", {})
            data_fields = ["facebook_post_id", "post_id", "page_name", "page_id", "user_name", "published_at"]
            for field in data_fields:
                if field in data:
                    print(f"   ✅ Data has {field}")
                else:
                    print(f"   ❌ Data missing {field}")
        
        # Test error response format
        error_data = {
            "title": "",  # Invalid title
            "description": "Testing error format",
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800",
            "product_url": "https://example.com/test-error"
        }
        
        error_success, error_response = self.run_test(
            "Response Format (Error)",
            "POST",
            "api/publishProduct",
            400,
            data=error_data
        )
        
        if error_success:
            # Check error response structure
            if "detail" in error_response:
                print(f"   ✅ Error response has detail field")
            else:
                print(f"   ❌ Error response missing detail field")
        
        self.tests_run += 1
        if success and error_success:
            self.tests_passed += 1
            return True
        return False

    def test_http_methods_validation(self):
        """Test that endpoints only accept correct HTTP methods"""
        print(f"\n🔍 Testing HTTP Methods Validation...")
        
        # Test GET on POST-only endpoint (should fail)
        try:
            response = requests.get(f"{self.base_url}/api/publishProduct")
            if response.status_code == 405:  # Method Not Allowed
                print("✅ GET correctly rejected on POST-only endpoint")
                method_validation_passed = True
            else:
                print(f"⚠️ GET on POST endpoint returned: {response.status_code}")
                method_validation_passed = False
        except Exception as e:
            print(f"❌ Error testing GET method: {e}")
            method_validation_passed = False
        
        # Test POST on GET-only endpoint (should fail)
        try:
            response = requests.post(f"{self.base_url}/api/publishProduct/config", json={})
            if response.status_code == 405:  # Method Not Allowed
                print("✅ POST correctly rejected on GET-only endpoint")
                method_validation_passed = method_validation_passed and True
            else:
                print(f"⚠️ POST on GET endpoint returned: {response.status_code}")
                method_validation_passed = False
        except Exception as e:
            print(f"❌ Error testing POST method: {e}")
            method_validation_passed = False
        
        self.tests_run += 1
        if method_validation_passed:
            self.tests_passed += 1
            return True
        return False

def main():
    print("🚀 Starting N8N Integration Tests for FacebookPost Application")
    print("=" * 70)
    
    tester = N8NIntegrationTester()
    
    # Run all tests in order
    tests = [
        # Setup
        tester.test_setup_test_user,
        
        # Configuration endpoint
        tester.test_get_config,
        
        # Main publishing endpoint - valid cases
        tester.test_publish_product_valid,
        tester.test_publish_product_with_api_key,
        tester.test_publish_product_without_user_page_ids,
        
        # Test endpoint
        tester.test_publish_product_test_endpoint,
        
        # Validation tests - missing/invalid data
        tester.test_publish_product_missing_title,
        tester.test_publish_product_empty_title,
        tester.test_publish_product_missing_description,
        tester.test_publish_product_invalid_image_url,
        tester.test_publish_product_invalid_product_url,
        
        # Error handling tests
        tester.test_publish_product_nonexistent_user,
        tester.test_publish_product_nonexistent_page,
        tester.test_publish_product_unreachable_image,
        
        # Format and method validation
        tester.test_response_format_consistency,
        tester.test_http_methods_validation,
        
        # Cleanup
        tester.test_cleanup_test_user
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            tester.tests_run += 1
    
    # Print final results
    print("\n" + "=" * 70)
    print(f"📊 N8N Integration Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All N8N integration tests passed!")
        print("✅ N8N integration is fully functional and ready for production")
        return 0
    else:
        failed_count = tester.tests_run - tester.tests_passed
        print(f"⚠️  {failed_count} tests failed")
        
        if failed_count > tester.tests_run * 0.5:  # More than 50% failed
            print("❌ More than 50% of N8N integration tests failed - major issues detected")
            print("❌ N8N integration is NOT ready for production")
            return 2
        else:
            print("⚠️  Minor issues detected in N8N integration - proceed with caution")
            print("⚠️  Review failed tests before production deployment")
            return 1

if __name__ == "__main__":
    sys.exit(main())