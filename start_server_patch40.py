#!/usr/bin/env python3
"""
Script de démarrage pour tester PATCH 40 - Correction Publications
"""
import os
import sys
import subprocess
import time

def main():
    print("=" * 60)
    print("🚀 DÉMARRAGE SERVEUR AVEC PATCH 40 - CORRECTION PUBLICATIONS")
    print("=" * 60)
    
    # Aller au répertoire backend
    os.chdir('/app/backend')
    
    print("📋 Informations PATCH 40:")
    print("   ✅ Correction extraction données webhook (store/shop_type)")
    print("   ✅ Support dual : webhook_handler + multipart direct")  
    print("   ✅ Auto-détection structure de données")
    print("   ✅ Publications Facebook + Instagram fonctionnelles")
    print("")
    
    print("🔧 Configuration détectée:")
    print(f"   • MongoDB: {os.getenv('MONGO_URL', 'Non configuré')}")
    print(f"   • FTP Host: {os.getenv('FTP_HOST', 'Non configuré')}")
    print(f"   • Ngrok: {os.getenv('ENABLE_NGROK', 'Non configuré')}")
    print("")
    
    print("🚀 Démarrage du serveur FastAPI...")
    print("📱 Les webhooks N8N devraient maintenant publier correctement !")
    print("🔍 Surveillez les logs pour les messages 'PATCH 40'")
    print("")
    
    try:
        # Démarrer le serveur
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "server:app", 
            "--host", "0.0.0.0", 
            "--port", "8001",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur serveur: {e}")

if __name__ == "__main__":
    main()