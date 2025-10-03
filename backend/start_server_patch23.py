#!/usr/bin/env python3
"""
PATCH 23 - Démarrage serveur avec corrections appliquées
Démarre le serveur avec les corrections de suppression de fichiers
"""

import os
import sys
import subprocess
import time
import signal

# Changer vers le répertoire backend
os.chdir('/app/backend')

def start_server():
    """Démarre le serveur avec les corrections PATCH 23"""
    print("🚀 PATCH 23: Démarrage serveur avec corrections...")
    
    try:
        # Lancer le serveur
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "server:app", 
            "--host", "0.0.0.0", 
            "--port", "8001",
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        print(f"✅ PATCH 23: Serveur démarré (PID: {process.pid})")
        print("📡 Serveur accessible sur: http://0.0.0.0:8001")
        print("🌐 Via ngrok: https://6885312f324f.ngrok-free.app")
        print("\n📋 PATCH 23: Corrections appliquées:")
        print("   - ✅ Suppression fichiers vidéo désactivée (ligne 4303)")
        print("   - ✅ Suppression fichiers temporaires désactivée (ligne 4734)")
        print("   - ✅ Fichiers conservés pour accès Facebook/Instagram")
        
        print("\n⏳ Serveur en cours d'exécution... Ctrl+C pour arrêter")
        
        # Afficher les logs en temps réel
        for line in process.stdout:
            print(f"[SERVER] {line.strip()}")
            
    except KeyboardInterrupt:
        print("\n🛑 PATCH 23: Arrêt serveur demandé")
        if process:
            process.terminate()
            process.wait()
        print("✅ PATCH 23: Serveur arrêté")
    
    except Exception as e:
        print(f"❌ PATCH 23: Erreur démarrage serveur: {e}")

if __name__ == "__main__":
    start_server()