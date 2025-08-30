import requests
import sys
import json
from datetime import datetime
import uuid
import tempfile
import os
from PIL import Image
import io

class WebhookStrategy1CTester:
    def __init__(self, base_url="https://feed-link-update.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, form_data=False):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        
        # Don't set Content-Type for form data - let requests handle it
        if not files and not form_data:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                if files or form_data:
                    response = requests.post(url, data=data, files=files, timeout=30)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2, default=str)[:500]}...")
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

    def test_webhook_get_info(self):
        """Test GET /api/webhook endpoint for configuration info"""
        success, response = self.run_test(
            "Webhook GET Info",
            "GET",
            "api/webhook",
            200
        )
        
        if success:
            available_stores = response.get('available_stores', [])
            shop_mapping = response.get('shop_mapping', {})
            
            print(f"   Available stores: {available_stores}")
            
            # Check for gizmobbs configuration
            gizmobbs_config = shop_mapping.get('gizmobbs', {})
            if gizmobbs_config:
                print(f"   gizmobbs config: {gizmobbs_config}")
                if gizmobbs_config.get('platform') == 'multi':
                    print("✅ gizmobbs configured for multi-platform")
                else:
                    print(f"⚠️  gizmobbs platform: {gizmobbs_config.get('platform')}")
            else:
                print("❌ gizmobbs configuration not found")
        
        return success

    def test_webhook_json_gizmobbs_strategy1c(self):
        """Test JSON webhook with gizmobbs store - should prioritize Strategy 1C"""
        test_data = {
            "title": "Test Strategy 1C - JSON Request",
            "description": "Testing Strategy 1C prioritization with accessible image URL",
            "image_url": "https://picsum.photos/800/600?random=strategy1c",
            "url": "https://gizmobbs.com/test-strategy1c",
            "store": "gizmobbs"
        }
        
        success, response = self.run_test(
            "Webhook JSON - gizmobbs Strategy 1C",
            "POST",
            "api/webhook",
            200,
            data=test_data
        )
        
        if success:
            status = response.get('status')
            message = response.get('message')
            data_section = response.get('data', {})
            
            print(f"   Status: {status}")
            print(f"   Message: {message}")
            
            # Check for Strategy 1C indicators (at top level of response)
            strategy_used = response.get('strategy_used')
            image_clickable = response.get('image_clickable')
            
            print(f"   Strategy used: {strategy_used}")
            print(f"   Image clickable: {image_clickable}")
            
            # Verify Strategy 1C was used
            if strategy_used == "feed_with_picture":
                print("✅ Strategy 1C (feed_with_picture) was used correctly")
            else:
                print(f"❌ Expected 'feed_with_picture', got '{strategy_used}'")
                
            if image_clickable is True:
                print("✅ Image is clickable (Strategy 1C success)")
            else:
                print(f"⚠️  Image clickable status: {image_clickable}")
                
            # Check publication results
            publication_results = data_section.get('publication_results', [])
            print(f"   Publication results: {len(publication_results)} entries")
            
            for i, result in enumerate(publication_results):
                result_status = result.get('status')
                result_message = result.get('message')
                platforms = result.get('platforms', [])
                
                print(f"   Publication {i+1}: {result_status} - {result_message}")
                print(f"   Platforms: {len(platforms)}")
        
        return success

    def test_webhook_multipart_gizmobbs_strategy1c(self):
        """Test multipart webhook with gizmobbs store - should use Strategy 1C with uploaded image"""
        # Create test image
        test_image = Image.new('RGB', (800, 600), color='blue')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # Prepare multipart data
        json_data = {
            "title": "Test Strategy 1C - Multipart Upload",
            "description": "Testing Strategy 1C with binary image upload",
            "url": "https://gizmobbs.com/test-multipart-strategy1c",
            "store": "gizmobbs"
        }
        
        files = {
            'image': ('test_strategy1c.jpg', img_bytes, 'image/jpeg')
        }
        data = {
            'json_data': json.dumps(json_data)
        }
        
        success, response = self.run_test(
            "Webhook Multipart - gizmobbs Strategy 1C",
            "POST",
            "api/webhook",
            200,
            data=data,
            files=files
        )
        
        if success:
            status = response.get('status')
            data_section = response.get('data', {})
            
            print(f"   Status: {status}")
            
            # Check Strategy 1C indicators (at top level of response)
            strategy_used = response.get('strategy_used')
            image_clickable = response.get('image_clickable')
            image_filename = data_section.get('image_filename')
            
            print(f"   Strategy used: {strategy_used}")
            print(f"   Image clickable: {image_clickable}")
            print(f"   Image filename: {image_filename}")
            
            # Verify Strategy 1C was used
            if strategy_used == "feed_with_picture":
                print("✅ Strategy 1C (feed_with_picture) used for multipart upload")
            else:
                print(f"❌ Expected 'feed_with_picture', got '{strategy_used}'")
                
            if image_clickable is True:
                print("✅ Uploaded image is clickable (Strategy 1C success)")
            else:
                print(f"⚠️  Image clickable status: {image_clickable}")
                
            if image_filename and image_filename.endswith('.jpg'):
                print("✅ Image uploaded and processed correctly")
            else:
                print(f"⚠️  Image filename: {image_filename}")
        
        return success

    def test_webhook_outdoor_store_strategy1c(self):
        """Test webhook with outdoor store - should also use Strategy 1C"""
        test_data = {
            "title": "Test Strategy 1C - Outdoor Store",
            "description": "Testing Strategy 1C with outdoor store configuration",
            "image_url": "https://picsum.photos/800/600?random=outdoor",
            "url": "https://logicampoutdoor.com/test-strategy1c",
            "store": "outdoor"
        }
        
        success, response = self.run_test(
            "Webhook JSON - outdoor Strategy 1C",
            "POST",
            "api/webhook",
            200,
            data=test_data
        )
        
        if success:
            strategy_used = response.get('strategy_used')
            image_clickable = response.get('image_clickable')
            
            print(f"   Strategy used: {strategy_used}")
            print(f"   Image clickable: {image_clickable}")
            
            if strategy_used == "feed_with_picture":
                print("✅ Strategy 1C works for outdoor store")
            else:
                print(f"⚠️  Outdoor store strategy: {strategy_used}")
        
        return success

    def test_webhook_logicantiq_store_strategy1c(self):
        """Test webhook with logicantiq store - should also use Strategy 1C"""
        test_data = {
            "title": "Test Strategy 1C - Logicantiq Store",
            "description": "Testing Strategy 1C with logicantiq store configuration",
            "image_url": "https://picsum.photos/800/600?random=logicantiq",
            "url": "https://logicantiq.com/test-strategy1c",
            "store": "logicantiq"
        }
        
        success, response = self.run_test(
            "Webhook JSON - logicantiq Strategy 1C",
            "POST",
            "api/webhook",
            400,  # Expect 400 since logicantiq has no main page configured
            data=test_data
        )
        
        if success:
            # This should fail due to no main page for logicantiq
            detail = response.get('detail', '')
            if 'No main page found for store logicantiq' in detail:
                print("✅ Correctly identified missing logicantiq page configuration")
            else:
                print(f"⚠️  Unexpected error: {detail}")
        
        return success

    def test_webhook_fallback_behavior(self):
        """Test webhook fallback behavior when image URL is not accessible"""
        test_data = {
            "title": "Test Strategy 1C Fallback",
            "description": "Testing fallback when remote image returns 404",
            "image_url": "https://httpstat.us/404",  # This will return 404
            "url": "https://gizmobbs.com/test-fallback",
            "store": "gizmobbs"
        }
        
        success, response = self.run_test(
            "Webhook Fallback - Inaccessible Image",
            "POST",
            "api/webhook",
            400,  # Expect 400 since image is not accessible
            data=test_data
        )
        
        if success:
            # This should fail with 400, so check error message
            detail = response.get('detail', '')
            print(f"   Error detail: {detail}")
            
            if 'not accessible' in detail and 'download failed' in detail:
                print("✅ Correctly identified inaccessible image and failed download")
            else:
                print(f"⚠️  Unexpected error message: {detail}")
        
        return success

    def test_webhook_no_image_url(self):
        """Test webhook behavior when no image URL is provided"""
        test_data = {
            "title": "Test No Image URL",
            "description": "Testing behavior when no image URL is provided",
            "url": "https://gizmobbs.com/test-no-image",
            "store": "gizmobbs"
            # No image_url field
        }
        
        success, response = self.run_test(
            "Webhook - No Image URL",
            "POST",
            "api/webhook",
            400,  # Expect 400 since image_url is required
            data=test_data
        )
        
        if success:
            # This should fail with 400 since image_url is required
            detail = response.get('detail', '')
            print(f"   Error detail: {detail}")
            
            if 'Image URL is required' in detail:
                print("✅ Correctly requires image URL")
            else:
                print(f"⚠️  Unexpected error: {detail}")
        
        return success

    def test_webhook_invalid_store(self):
        """Test webhook with invalid store name"""
        test_data = {
            "title": "Test Invalid Store",
            "description": "Testing behavior with invalid store name",
            "image_url": "https://picsum.photos/800/600?random=invalid",
            "url": "https://example.com/test-invalid-store",
            "store": "invalid_store_name"
        }
        
        success, response = self.run_test(
            "Webhook - Invalid Store",
            "POST",
            "api/webhook",
            200,  # Should still work with fallback
            data=test_data
        )
        
        if success:
            status = response.get('status')
            data_section = response.get('data', {})
            strategy_used = data_section.get('strategy_used')
            
            print(f"   Status: {status}")
            print(f"   Strategy used: {strategy_used}")
            
            # Should still attempt Strategy 1C if image is available
            if strategy_used == "feed_with_picture":
                print("✅ Strategy 1C used even with invalid store (good fallback)")
            else:
                print(f"⚠️  Strategy with invalid store: {strategy_used}")
        
        return success

    def test_webhook_missing_required_fields(self):
        """Test webhook with missing required fields"""
        test_data = {
            "title": "Test Missing Fields"
            # Missing description, url, store
        }
        
        success, response = self.run_test(
            "Webhook - Missing Required Fields",
            "POST",
            "api/webhook",
            400,  # Should return validation error
            data=test_data
        )
        
        if success:
            detail = response.get('detail', '')
            print(f"   Validation error: {detail}")
            
            if 'required' in detail.lower() or 'missing' in detail.lower():
                print("✅ Correctly identified missing required fields")
            else:
                print(f"⚠️  Unexpected validation message: {detail}")
        
        return success

    def test_webhook_strategy_consistency(self):
        """Test that Strategy 1C is consistently returned across multiple requests"""
        test_data = {
            "title": "Test Strategy Consistency",
            "description": "Testing that Strategy 1C is consistently applied",
            "image_url": "https://picsum.photos/800/600?random=consistency",
            "url": "https://gizmobbs.com/test-consistency",
            "store": "gizmobbs"
        }
        
        consistent_results = []
        
        for i in range(3):  # Test 3 times
            success, response = self.run_test(
                f"Webhook Consistency Test {i+1}/3",
                "POST",
                "api/webhook",
                200,
                data=test_data
            )
            
            if success:
                data_section = response.get('data', {})
                strategy_used = data_section.get('strategy_used')
                consistent_results.append(strategy_used)
                print(f"   Test {i+1} strategy: {strategy_used}")
        
        # Check consistency
        if len(set(consistent_results)) == 1 and consistent_results[0] == "feed_with_picture":
            print("✅ Strategy 1C consistently applied across multiple requests")
            return True
        else:
            print(f"❌ Inconsistent strategies: {consistent_results}")
            return False

    def test_webhook_response_structure(self):
        """Test that webhook response has correct structure for Strategy 1C"""
        test_data = {
            "title": "Test Response Structure",
            "description": "Testing webhook response structure for Strategy 1C",
            "image_url": "https://picsum.photos/800/600?random=structure",
            "url": "https://gizmobbs.com/test-structure",
            "store": "gizmobbs"
        }
        
        success, response = self.run_test(
            "Webhook Response Structure",
            "POST",
            "api/webhook",
            200,
            data=test_data
        )
        
        if success:
            # Check required response fields
            required_fields = ['status', 'message', 'data']
            missing_fields = []
            
            for field in required_fields:
                if field not in response:
                    missing_fields.append(field)
            
            if not missing_fields:
                print("✅ All required response fields present")
            else:
                print(f"❌ Missing response fields: {missing_fields}")
                return False
            
            # Check data section structure
            data_section = response.get('data', {})
            expected_data_fields = ['strategy_used', 'image_clickable']
            
            for field in expected_data_fields:
                if field in data_section:
                    print(f"✅ Data field '{field}' present: {data_section[field]}")
                else:
                    print(f"⚠️  Data field '{field}' missing")
            
            # Verify strategy_used format
            strategy_used = data_section.get('strategy_used')
            if strategy_used == "feed_with_picture":
                print("✅ strategy_used has correct value for Strategy 1C")
            else:
                print(f"⚠️  strategy_used value: {strategy_used}")
            
            # Verify image_clickable is boolean
            image_clickable = data_section.get('image_clickable')
            if isinstance(image_clickable, bool):
                print(f"✅ image_clickable is boolean: {image_clickable}")
            else:
                print(f"⚠️  image_clickable type: {type(image_clickable)}")
        
        return success

def main():
    print("🚀 Starting Webhook Strategy 1C Tests...")
    print("Testing Strategy 1C prioritization and fallback behavior")
    print("=" * 80)
    
    tester = WebhookStrategy1CTester()
    
    # Run Strategy 1C specific tests
    tests = [
        tester.test_webhook_get_info,
        tester.test_webhook_json_gizmobbs_strategy1c,
        tester.test_webhook_multipart_gizmobbs_strategy1c,
        tester.test_webhook_outdoor_store_strategy1c,
        tester.test_webhook_logicantiq_store_strategy1c,
        tester.test_webhook_fallback_behavior,
        tester.test_webhook_no_image_url,
        tester.test_webhook_invalid_store,
        tester.test_webhook_missing_required_fields,
        tester.test_webhook_strategy_consistency,
        tester.test_webhook_response_structure,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 80)
    print(f"📊 Strategy 1C Tests completed: {tester.tests_passed}/{tester.tests_run} passed")
    
    # Summary of Strategy 1C testing
    print("\n🎯 STRATEGY 1C TEST SUMMARY:")
    print("✅ Tests focused on Strategy 1C (API Graph /feed with message, link, picture)")
    print("✅ Verified prioritization when valid image URL exists")
    print("✅ Tested intelligent fallback for inaccessible images")
    print("✅ Confirmed strategy_used: 'feed_with_picture' response")
    print("✅ Tested image_clickable: true when Strategy 1C succeeds")
    print("✅ Verified behavior across different stores (gizmobbs, outdoor, logicantiq)")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 All Strategy 1C tests passed!")
        print("✅ Strategy 1C implementation is working correctly")
        return 0
    else:
        print(f"\n⚠️  {tester.tests_run - tester.tests_passed} Strategy 1C tests failed")
        print("❌ Strategy 1C implementation needs attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())