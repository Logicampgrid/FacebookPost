#!/usr/bin/env python3
"""
Test avec URL ngrok simulée dans frontend/.env
"""

import sys
import os
import shutil
sys.path.insert(0, '/app/backend')

def test_with_ngrok_url():
    """Test la détection avec une URL ngrok simulée"""
    print("=== TEST AVEC URL NGROK SIMULÉE ===")
    
    # Sauvegarde de l'ancien .env
    env_path = "/app/frontend/.env"
    backup_path = "/app/frontend/.env.backup"
    
    try:
        # Sauvegarder le fichier actuel
        shutil.copy2(env_path, backup_path)
        
        # Créer un nouveau .env avec une URL ngrok
        with open(env_path, 'w') as f:
            f.write("REACT_APP_BACKEND_URL=https://abc123.ngrok-free.app\n")
            f.write("DANGEROUSLY_DISABLE_HOST_CHECK=true\n")
            f.write("ESLINT_NO_DEV_ERRORS=true\n")
            f.write("HOST=0.0.0.0\n")
            f.write("PORT=3000\n")
            f.write("BROWSER=none\n")
        
        print("📝 URL ngrok simulée configurée: https://abc123.ngrok-free.app")
        
        # Recharger le module server
        import importlib
        import server
        importlib.reload(server)
        
        # Test de détection
        backend_url = server.get_active_ngrok_url()
        print(f"🔍 URL détectée: {backend_url}")
        
        # Test de l'URI de redirection webhook
        redirect_uri = server.build_dynamic_redirect_uri("/api/webhook")
        print(f"🎯 URI webhook: {redirect_uri}")
        
        if backend_url == "https://abc123.ngrok-free.app":
            print("✅ URL ngrok simulée détectée correctement")
            
            if redirect_uri == "https://abc123.ngrok-free.app/api/webhook":
                print("✅ URI webhook correcte: https://abc123.ngrok-free.app/api/webhook")
                return True
            else:
                print(f"❌ URI webhook incorrecte: {redirect_uri}")
                return False
        else:
            print(f"❌ URL détectée incorrecte: {backend_url}")
            return False
            
    finally:
        # Restaurer le fichier original
        if os.path.exists(backup_path):
            shutil.move(backup_path, env_path)
            print("🔄 Fichier .env original restauré")

if __name__ == "__main__":
    success = test_with_ngrok_url()
    sys.exit(0 if success else 1)