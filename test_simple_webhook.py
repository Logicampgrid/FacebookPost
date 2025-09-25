#!/usr/bin/env python3
"""
Test simple du webhook pour valider la correction Instagram
"""

import requests
import json

def test_simple_webhook():
    """Test basique sans fichier pour vérifier le fonctionnement"""
    
    print("🧪 Test webhook simple...")
    
    # Données de test similaires aux logs
    webhook_data = {
        "store": "gizmobbs",
        "title": "Test correction Instagram - Produit simple",
        "url": "https://www.logicamp.org/wordpress/produit/test/",
        "description": "simple"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/api/webhook",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text[:500]}...")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_webhook()
    if success:
        print("✅ Test webhook simple réussi")
    else:
        print("❌ Test webhook simple échoué")