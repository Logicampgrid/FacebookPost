# Configuration spécifique pour l'usage local Windows
# Ce fichier peut remplacer server.py pour un usage 100% local

import os
from dotenv import load_dotenv

# Force le mode local
load_dotenv()

# Override des variables d'environnement pour usage local
os.environ["ENABLE_NGROK"] = "false"
os.environ["MONGO_URL"] = "mongodb://localhost:27017"
os.environ["PUBLIC_BASE_URL"] = "http://localhost:8001"
os.environ["EXTERNAL_WEBHOOK_ENABLED"] = "false"

# Import du serveur principal avec configuration locale
from server import *

if __name__ == "__main__":
    import uvicorn
    print("🏠 Démarrage en mode LOCAL Windows")
    print("🌐 Application disponible sur : http://localhost:8001")
    print("📊 API Health Check : http://localhost:8001/api/health")
    print("⚠️  Mode NGROK désactivé pour usage local")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")