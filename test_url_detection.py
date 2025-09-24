#!/usr/bin/env python3
"""
Test de la détection de l'URL backend avec priorité au frontend/.env
"""

import sys
sys.path.insert(0, '/app/backend')

from server import get_active_ngrok_url, build_dynamic_redirect_uri

def test_url_detection():
    """Test la détection d'URL avec priorité au frontend/.env"""
    print("=== TEST DÉTECTION URL BACKEND ===")
    
    # Test get_active_ngrok_url()
    backend_url = get_active_ngrok_url()
    print(f"🔍 URL détectée: {backend_url}")
    
    if backend_url:
        print("✅ URL backend détectée avec succès")
        
        # Test build_dynamic_redirect_uri()
        redirect_uri = build_dynamic_redirect_uri("/api/webhook")
        print(f"🎯 URI de redirection pour webhook: {redirect_uri}")
        
        if redirect_uri:
            print("✅ URI de redirection construite avec succès")
            return True
        else:
            print("❌ Échec construction URI de redirection")
            return False
    else:
        print("❌ Aucune URL backend détectée")
        return False

if __name__ == "__main__":
    success = test_url_detection()
    sys.exit(0 if success else 1)