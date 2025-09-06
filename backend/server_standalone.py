#!/usr/bin/env python3
"""
Script pour lancer le serveur FastAPI en mode standalone sur le port 8765
Usage: python server_standalone.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import app

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Démarrage du serveur FacebookPost en mode standalone")
    print("📍 Backend + Frontend combinés sur FastAPI")
    print("🌐 Serveur disponible sur: http://localhost:8765")
    print("📁 Frontend React servi à la racine /")
    print("🔗 API endpoints disponibles sur /api/*")
    print("✅ CORS activé pour toutes les origines")
    print("-" * 60)
    
    # Désactiver ngrok en mode standalone
    os.environ["ENABLE_NGROK"] = "false"
    
    uvicorn.run(app, host="0.0.0.0", port=8765)