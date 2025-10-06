#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug NoneType error - Test simple pour identifier l'erreur
"""

import requests
import json

def test_simple_webhook():
    """Test simple pour debug NoneType"""
    
    # Test minimal avec données valides
    minimal_data = {
        "store": "gizmobbs",
        "title": "Test Debug",
        "url": "https://example.com", 
        "description": "Test description"
    }
    
    print(f"🔍 Test minimal webhook")
    
    try:
        response = requests.post(
            "http://localhost:8001/api/webhook",
            data={
                "jsonData": json.dumps(minimal_data)
            },
            files={"file": ("test.jpg", b"fake", "image/jpeg")},
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    test_simple_webhook()