#!/usr/bin/env python3
"""
Test script to validate the n8n webhook fix
Simulates what n8n should send to the Instagram webhook
"""

import requests
import json
import os
from datetime import datetime

def test_webhook_with_binary_data():
    """Test the webhook with proper multipart form data"""
    print("🧪 Testing Instagram Webhook with Binary Data")
    print("=" * 50)
    
    # Find a test image
    test_images = [
        "/app/backend/uploads/webhook_054c8223_1755452509.jpg",
        "/app/backend/uploads/c1481342-261c-463e-9f38-4495d2c83533.jpg",
        "/app/backend/test_image.jpg"
    ]
    
    test_image = None
    for img_path in test_images:
        if os.path.exists(img_path):
            test_image = img_path
            break
    
    if not test_image:
        print("❌ No test image found")
        return False
    
    print(f"📸 Using test image: {test_image}")
    
    # Prepare the data exactly as n8n should send it
    webhook_url = "https://social-media-bridge.preview.emergentagent.com/api/webhook"
    
    # JSON data as string (this is how n8n sends it)
    json_data = {
        "title": "N8N Test Product - Fixed Binary Data",
        "description": "This is a test product published via n8n workflow after fixing the binary data error. The image should be properly attached as multipart form data.",
        "url": "https://gizmobbs.com/test-product-n8n",
        "store": "gizmobbs"
    }
    
    json_string = json.dumps(json_data)
    
    try:
        # Open the image file in binary mode
        with open(test_image, 'rb') as image_file:
            # Prepare multipart form data
            files = {
                'image': ('test_image.jpg', image_file, 'image/jpeg'),
                'json_data': (None, json_string, 'application/json')
            }
            
            print(f"🚀 Sending POST request to: {webhook_url}")
            print(f"📋 JSON Data: {json_string}")
            
            # Send the request (this simulates what n8n HTTP Request node should do)
            response = requests.post(webhook_url, files=files, timeout=30)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print("✅ SUCCESS! Webhook processed correctly")
                    print(f"📁 Image saved as: {result['data']['image_filename']}")
                    print(f"📸 Image size: {result['data']['image_size_bytes']} bytes")
                    
                    if 'publication_results' in result['data']:
                        pub_results = result['data']['publication_results'][0]
                        print(f"📢 Publication status: {pub_results['status']}")
                        
                        if 'details' in pub_results:
                            details = pub_results['details']
                            print(f"📘 Facebook post: {details.get('facebook_post_id', 'Failed')}")
                            print(f"📱 Instagram post: {details.get('instagram_post_id', 'Failed - ' + str(details.get('instagram_error', 'Unknown error')))}")
                            print(f"👤 Published by: {details.get('user_name', 'Unknown')}")
                    
                    return True
                    
                except json.JSONDecodeError:
                    print("❌ Invalid JSON response")
                    print(f"Response: {response.text[:500]}")
                    return False
            else:
                print(f"❌ HTTP Error {response.status_code}")
                print(f"Response: {response.text[:500]}")
                return False
                
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Test image not found: {test_image}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_n8n_configuration():
    """Show the correct n8n HTTP Request node configuration"""
    print("\n🔧 N8N HTTP REQUEST NODE CONFIGURATION")
    print("=" * 50)
    
    config = """
    CORRECT CONFIGURATION FOR N8N HTTP REQUEST NODE:
    
    1. Method: POST
    2. URL: https://social-media-bridge.preview.emergentagent.com/api/webhook
    3. Content Type: multipart-form-data
    4. Body Parameters:
       
       Parameter 1:
       - Name: image
       - Type: Form Binary Data
       - Input Data Field Name: data
       
       Parameter 2:
       - Name: json_data
       - Type: Form Data
       - Value: {"title": "{{ $json.title }}", "description": "{{ $json.description }}", "url": "{{ $json.url }}", "store": "gizmobbs"}
    
    COMMON ERRORS TO AVOID:
    ❌ Using 'attachment' instead of 'data' for binary field name
    ❌ Using 'application/json' content type instead of 'multipart-form-data'
    ❌ Not setting image parameter to 'Form Binary Data' type
    ❌ Missing binary data from previous node
    """
    
    print(config)

def test_alternative_approaches():
    """Test alternative approaches for n8n integration"""
    print("\n🔄 ALTERNATIVE APPROACHES FOR N8N")
    print("=" * 50)
    
    approaches = """
    IF BINARY DATA STILL DOESN'T WORK:
    
    1. USE DIRECT FILE UPLOAD:
       - Use 'Read Binary File' node first
       - Ensure output field is named 'data'
    
    2. USE URL DOWNLOAD APPROACH:
       - Download image with HTTP Request (responseFormat: file)
       - Chain directly to Instagram webhook request
    
    3. USE BASE64 ENCODING:
       - Convert binary to base64 in Set node
       - Send as regular form data field
    
    4. DEBUG BINARY DATA:
       - Add Set node before HTTP Request
       - Check if $binary.data exists
       - Verify field names match exactly
    """
    
    print(approaches)

if __name__ == "__main__":
    print("🎯 N8N WEBHOOK FIX VALIDATOR")
    print("Testing Instagram webhook integration")
    print(f"⏰ Test started at: {datetime.now()}")
    print()
    
    # Test the webhook functionality
    success = test_webhook_with_binary_data()
    
    # Show configuration regardless of test result
    show_n8n_configuration()
    test_alternative_approaches()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ WEBHOOK TEST SUCCESSFUL!")
        print("Your n8n configuration should work with the provided settings.")
    else:
        print("⚠️ WEBHOOK TEST HAD ISSUES")
        print("Please check the configuration guide above.")
    
    print("\n📚 QUICK REFERENCE:")
    print("- Guide: /app/N8N_WEBHOOK_FIX_GUIDE.md")
    print("- Workflow: /app/n8n_instagram_webhook_workflow.json")
    print("- Test script: /app/test_n8n_webhook_fix.py")