#!/usr/bin/env python3
"""
Test de validation PATCH 24 - Système suppression différée
"""

import requests
import os
import time
from pathlib import Path

def test_patch24_delayed_cleanup():
    """Teste que les fichiers ne sont plus supprimés immédiatement"""
    
    print("🧪 PATCH 24: Test du système de suppression différée")
    
    # Configuration
    backend_url = "http://localhost:8001"
    
    # Créer un fichier test simple
    test_content = "Test PATCH 24 - Validation suppression différée"
    
    # Tester avec endpoint webhook
    webhook_data = {
        "store": "gizmobbs", 
        "title": "Test PATCH 24 Suppression Différée",
        "url": "https://example.com/test-patch24",
        "description": "Test validation du système de suppression différée des fichiers"
    }
    
    # Créer un fichier image factice
    test_image_path = "/app/backend/test_patch24.txt"
    with open(test_image_path, 'w') as f:
        f.write(test_content)
    
    try:
        # Tester l'endpoint webhook
        print(f"📤 Envoi webhook test vers {backend_url}/api/webhook")
        
        with open(test_image_path, 'rb') as test_file:
            files = {'file': ('test_patch24.txt', test_file, 'text/plain')}
            response = requests.post(
                f"{backend_url}/api/webhook",
                data=webhook_data,
                files=files,
                timeout=30
            )
        
        print(f"📥 Réponse: Status {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook traité: {result.get('status', 'N/A')}")
            
            # Vérifier que des fichiers ont été créés et ne sont PAS supprimés immédiatement
            uploads_dir = "/app/backend/uploads"
            webhook_files = [f for f in os.listdir(uploads_dir) if f.startswith("webhook_") and "patch24" in f.lower()]
            
            if webhook_files:
                print(f"✅ PATCH 24: {len(webhook_files)} fichiers webhook trouvés (non supprimés)")
                for file in webhook_files[:3]:  # Montrer les 3 premiers
                    file_path = os.path.join(uploads_dir, file)
                    if os.path.exists(file_path):
                        size = os.path.getsize(file_path)
                        print(f"  📁 {file} ({size} bytes) - CONSERVÉ ✅")
                
                print("✅ PATCH 24: Suppression immédiate supprimée avec succès!")
                print("⏰ Les fichiers seront nettoyés automatiquement dans 2h")
            else:
                print("⚠️ Aucun fichier webhook détecté")
            
        else:
            print(f"❌ Erreur webhook: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    finally:
        # Nettoyer le fichier test
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
    
    print("🏁 Test PATCH 24 terminé")

if __name__ == "__main__":
    test_patch24_delayed_cleanup()