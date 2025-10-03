#!/usr/bin/env python3
"""
PATCH 23 - Test simple du servage de fichiers statiques
Test si FastAPI StaticFiles peut servir les fichiers correctement
"""

import os
import time
import requests
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import threading

def test_staticfiles_simple():
    """Test simple de StaticFiles FastAPI"""
    
    # Créer une app FastAPI simple
    app = FastAPI(title="Test PATCH 23 StaticFiles")
    
    # Monter le dossier uploads
    uploads_path = "/app/backend/uploads"
    if os.path.exists(uploads_path):
        app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")
        print(f"✅ Dossier uploads monté: {uploads_path}")
    else:
        print(f"❌ Dossier uploads non trouvé: {uploads_path}")
        return
    
    # Créer un fichier de test
    test_file = "test_staticfiles_patch23.mp4"
    test_path = os.path.join(uploads_path, test_file)
    
    with open(test_path, "wb") as f:
        f.write(b"Test content for StaticFiles PATCH 23")
    
    print(f"✅ Fichier de test créé: {test_file}")
    
    # Route de test
    @app.get("/test")
    async def test():
        return {"message": "Test PATCH 23", "file": test_file}
    
    # Démarrer le serveur dans un thread
    def run_server():
        uvicorn.run(app, host="0.0.0.0", port=8002, log_level="warning")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Attendre que le serveur démarre
    time.sleep(3)
    
    # Tester l'accès au fichier
    try:
        response = requests.get(f"http://localhost:8002/uploads/{test_file}", timeout=5)
        print(f"📡 Test accès local: Status {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Contenu reçu: {len(response.content)} bytes")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur test local: {e}")
    
    # Test via ngrok si disponible
    try:
        ngrok_test = requests.get("https://6885312f324f.ngrok-free.app/uploads/test_image.jpg", timeout=10)
        print(f"🌐 Test ngrok (image existante): Status {ngrok_test.status_code}")
    except Exception as e:
        print(f"⚠️ Test ngrok échoué: {e}")
    
    # Nettoyage
    try:
        os.remove(test_path)
        print("🧹 Fichier de test supprimé")
    except:
        pass

if __name__ == "__main__":
    print("🚀 PATCH 23 - Test StaticFiles FastAPI")
    print("=" * 50)
    test_staticfiles_simple()
    print("✅ Test terminé")