#!/usr/bin/env python3
"""
DÉMARRAGE AUTOMATIQUE GIZMO
Lance le serveur et active immédiatement la surveillance automatique
"""

import sys
import time
import requests
import subprocess
import os
from pathlib import Path

def wait_for_server(base_url="http://localhost:8001", max_wait=60):
    """Attend que le serveur soit prêt"""
    print("⏳ Attente du démarrage du serveur...")
    
    for i in range(max_wait):
        try:
            response = requests.get(f"{base_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Serveur prêt!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"   Tentative {i+1}/{max_wait}...")
        time.sleep(1)
    
    print("❌ Timeout: serveur non disponible")
    return False

def activate_auto_watcher(base_url="http://localhost:8001"):
    """Active la surveillance automatique"""
    try:
        print("🔍 Activation de la surveillance automatique...")
        
        response = requests.post(f"{base_url}/api/folder-watcher/start", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Surveillance automatique activée!")
                print(f"📁 Stores surveillés: {', '.join(result.get('watched_stores', []))}")
                return True
            else:
                print(f"⚠️ Surveillance déjà active: {result.get('message')}")
                return True
        else:
            print(f"❌ Erreur activation surveillance: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur activation surveillance: {e}")
        return False

def check_directories():
    """Vérifie et crée les dossiers nécessaires"""
    directories = [
        "C:/gizmobbs/download",
        "C:/gizmobbs/processed", 
        "C:/logicantiq/download",
        "C:/logicantiq/processed",
        "C:/outdoor/download",
        "C:/outdoor/processed"
    ]
    
    print("📁 Vérification des dossiers...")
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Dossier prêt: {directory}")
        except Exception as e:
            print(f"⚠️ Erreur création {directory}: {e}")

def main():
    """Fonction principale"""
    print("🚀 DÉMARRAGE AUTOMATIQUE GIZMO MANAGER")
    print("=" * 50)
    
    # Vérifier les dossiers
    check_directories()
    
    # Vérifier si le serveur est déjà démarré
    try:
        response = requests.get("http://localhost:8001/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Serveur déjà démarré")
            server_ready = True
        else:
            server_ready = False
    except:
        server_ready = False
    
    if not server_ready:
        print("🔄 Démarrage du serveur...")
        # Note: En mode conteneur, on suppose que le serveur est géré par supervisor
        # Attendre que le serveur soit prêt
        server_ready = wait_for_server()
    
    if server_ready:
        # Activer la surveillance automatique
        if activate_auto_watcher():
            print("\n🎉 SYSTÈME PRÊT!")
            print("=" * 30)
            print("📁 La surveillance automatique est active")
            print("🔄 Les fichiers ajoutés aux dossiers seront automatiquement traités")
            print("📱 Publication avec retry Instagram et fallback Facebook")
            print("\n📋 Dossiers surveillés:")
            print("   • C:/gizmobbs/download")
            print("   • C:/logicantiq/download") 
            print("   • C:/outdoor/download")
            print("\n💡 Utilisez gizmo_manager.py pour le contrôle manuel")
            
            # Garder le script actif
            try:
                print("\n⏸️  Appuyez sur Ctrl+C pour arrêter")
                while True:
                    time.sleep(60)
                    # Vérifier périodiquement que la surveillance est active
                    try:
                        response = requests.get("http://localhost:8001/api/folder-watcher/status", timeout=5)
                        if response.status_code == 200:
                            status = response.json()
                            if not status.get("status", {}).get("running", False):
                                print("⚠️ Surveillance interrompue, redémarrage...")
                                activate_auto_watcher()
                    except:
                        pass
                        
            except KeyboardInterrupt:
                print("\n🛑 Arrêt demandé")
                try:
                    response = requests.post("http://localhost:8001/api/folder-watcher/stop", timeout=10)
                    if response.status_code == 200:
                        print("✅ Surveillance arrêtée proprement")
                    else:
                        print("⚠️ Erreur arrêt surveillance")
                except:
                    print("⚠️ Impossible d'arrêter la surveillance proprement")
        else:
            print("❌ Impossible d'activer la surveillance automatique")
            sys.exit(1)
    else:
        print("❌ Serveur non disponible")
        sys.exit(1)

if __name__ == "__main__":
    main()