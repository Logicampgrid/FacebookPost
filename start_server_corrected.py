#!/usr/bin/env python3
"""
Script de démarrage du serveur FacebookPost corrigé
"""
import os
import sys
import subprocess
import signal
import time

# Ajouter le chemin backend
sys.path.insert(0, '/app/backend')

def cleanup_processes():
    """Nettoyer les processus ngrok et serveur existants"""
    print("🧹 Nettoyage des processus existants...")
    
    # Tuer les processus Python
    try:
        subprocess.run(["pkill", "-f", "uvicorn"], capture_output=True)
        subprocess.run(["pkill", "-f", "server_windows"], capture_output=True)
    except:
        pass
    
    # Tuer les processus ngrok
    try:
        subprocess.run(["pkill", "-f", "ngrok"], capture_output=True)
    except:
        pass
    
    time.sleep(2)
    print("✅ Nettoyage terminé")

def start_server():
    """Démarrer le serveur avec notre version corrigée"""
    try:
        print("🚀 Démarrage du serveur FacebookPost corrigé...")
        
        # Importer et démarrer le serveur
        import uvicorn
        from server_windows import app
        
        print("✅ Modules importés avec succès")
        print("🌐 Serveur accessible sur http://localhost:8001")
        print("📊 Health check: http://localhost:8001/api/health")
        print("🏪 Stores: http://localhost:8001/api/stores")
        print("")
        print("Appuyez sur Ctrl+C pour arrêter le serveur")
        
        # Démarrer le serveur
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur démarrage serveur: {e}")
    finally:
        print("🧹 Nettoyage final...")
        cleanup_processes()

if __name__ == "__main__":
    cleanup_processes()
    start_server()