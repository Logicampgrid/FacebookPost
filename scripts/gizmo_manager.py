#!/usr/bin/env python3
"""
GIZMO MANAGER - Client de gestion pour FacebookPost
Script client pour gérer la publication automatique des médias Gizmo
avec retry Instagram et fallback Facebook
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Optional

class GizmoManager:
    """Client de gestion pour le système FacebookPost"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Effectue une requête HTTP avec gestion d'erreurs"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Erreur HTTP: {str(e)}"}
        except json.JSONDecodeError:
            return {"success": False, "error": "Réponse non-JSON"}
    
    def get_server_status(self) -> dict:
        """Vérifie le statut du serveur"""
        return self._make_request("GET", "/api/health")
    
    def get_poster_media_status(self) -> dict:
        """Récupère le statut de poster_media pour tous les stores"""
        return self._make_request("GET", "/api/poster-media/status")
    
    def trigger_publication(self, store: Optional[str] = None) -> dict:
        """Déclenche la publication pour un store ou tous les stores"""
        if store:
            return self._make_request("POST", f"/api/poster-media/{store}")
        else:
            return self._make_request("POST", "/api/poster-media")
    
    def start_folder_watcher(self) -> dict:
        """Démarre la surveillance automatique des dossiers"""
        return self._make_request("POST", "/api/folder-watcher/start")
    
    def stop_folder_watcher(self) -> dict:
        """Arrête la surveillance automatique des dossiers"""
        return self._make_request("POST", "/api/folder-watcher/stop")
    
    def get_watcher_status(self) -> dict:
        """Récupère le statut de la surveillance des dossiers"""
        return self._make_request("GET", "/api/folder-watcher/status")
    
    def display_status(self, status_data: dict):
        """Affiche le statut de manière formatée"""
        if not status_data.get("success"):
            print(f"❌ Erreur: {status_data.get('error', 'Erreur inconnue')}")
            return
        
        status = status_data.get("status", {})
        summary = status_data.get("summary", {})
        
        print("📊 STATUT POSTER MEDIA ENHANCED")
        print("=" * 50)
        print(f"🏪 Stores totaux: {summary.get('total_stores', 0)}")
        print(f"✅ Stores prêts: {summary.get('ready_stores', 0)}")
        print(f"📁 Fichiers prêts: {summary.get('total_files_ready', 0)}")
        print(f"🌐 FTP configuré: {'✅ Oui' if summary.get('ftp_configured') else '❌ Non'}")
        
        # Détails par store
        stores_data = status.get("stores", {})
        for store_name, store_info in stores_data.items():
            print(f"\n🏪 {store_info['name']} ({store_name})")
            print(f"   📁 Dossier: {store_info['download_dir']}")
            print(f"   📁 Existe: {'✅ Oui' if store_info['download_dir_exists'] else '❌ Non'}")
            print(f"   🔑 Token: {'✅ Oui' if store_info['access_token_configured'] else '❌ Non'}")
            print(f"   📱 Instagram ID: {'✅ Oui' if store_info['ig_user_id_configured'] else '❌ Non'}")
            print(f"   📄 Fichiers: {store_info['files_count']}")
            print(f"   🚀 Prêt: {'✅ Oui' if store_info['ready_to_process'] else '❌ Non'}")
            
            # Aperçu des fichiers
            files_ready = store_info.get("files_ready", [])
            if files_ready:
                print(f"   📋 Fichiers prêts (aperçu):")
                for file_info in files_ready[:3]:  # Max 3 pour l'affichage
                    print(f"      • {file_info['filename']} ({file_info['size_mb']} MB)")
                if len(files_ready) > 3:
                    print(f"      ... et {len(files_ready) - 3} autres")
    
    def display_watcher_status(self, status_data: dict):
        """Affiche le statut de la surveillance"""
        if not status_data.get("success"):
            print(f"❌ Erreur surveillance: {status_data.get('error', 'Erreur inconnue')}")
            return
        
        status = status_data.get("status", {})
        
        print("\n🔍 STATUT SURVEILLANCE AUTOMATIQUE")
        print("=" * 50)
        print(f"🔄 Surveillance active: {'✅ Oui' if status.get('running') else '❌ Non'}")
        print(f"📁 Dossiers surveillés: {status.get('total_watchers', 0)}")
        
        watched_stores = status.get("watched_stores", [])
        if watched_stores:
            print(f"🏪 Stores surveillés: {', '.join(watched_stores)}")
        
        handlers_status = status.get("handlers_status", {})
        if handlers_status:
            print("\n📊 Détails par store:")
            for store, handler_info in handlers_status.items():
                print(f"   • {store}: {handler_info['processing_files']} en cours, {handler_info['last_processed_count']} traités")
    
    def display_publication_result(self, result_data: dict):
        """Affiche le résultat de publication"""
        if not result_data.get("success"):
            print(f"❌ Publication échouée: {result_data.get('error', 'Erreur inconnue')}")
            return
        
        result = result_data.get("result", {})
        stats = result.get("stats", {})
        
        print("\n🎯 RÉSULTAT DE LA PUBLICATION")
        print("=" * 50)
        print(f"✅ Succès: {result_data.get('success')}")
        print(f"⏰ Timestamp: {result_data.get('timestamp', 'N/A')}")
        print(f"💬 Message: {result.get('message', 'N/A')}")
        
        if stats:
            print(f"\n📊 STATISTIQUES GLOBALES")
            print("=" * 30)
            print(f"🏪 Stores traités: {stats.get('stores_processed', 0)}")
            print(f"📁 Fichiers trouvés: {stats.get('total_files_found', 0)}")
            print(f"⚙️  Fichiers traités: {stats.get('total_files_processed', 0)}")
            print(f"✅ Fichiers publiés: {stats.get('total_files_published', 0)}")
            print(f"❌ Fichiers échoués: {stats.get('total_files_failed', 0)}")
            
            # Détails par store
            store_results = stats.get("store_results", {})
            for store_name, store_stats in store_results.items():
                if store_stats.get("files_processed", 0) > 0:
                    print(f"\n🏪 {store_name.upper()}:")
                    print(f"   📁 Trouvés: {store_stats.get('files_found', 0)}")
                    print(f"   ⚙️  Traités: {store_stats.get('files_processed', 0)}")
                    print(f"   ✅ Publiés: {store_stats.get('files_published', 0)}")
                    print(f"   ❌ Échoués: {store_stats.get('files_failed', 0)}")
                    
                    # Afficher les erreurs
                    errors = store_stats.get("errors", [])
                    if errors:
                        print(f"   ⚠️  Erreurs:")
                        for error in errors[:3]:  # Max 3 erreurs
                            print(f"      • {error}")

def main():
    """Fonction principale - Interface en ligne de commande"""
    print("🚀 GIZMO MANAGER - Client FacebookPost Enhanced")
    print("=" * 60)
    
    manager = GizmoManager()
    
    while True:
        print("\n📋 MENU PRINCIPAL")
        print("1. 📊 Vérifier le statut")
        print("2. 🚀 Déclencher publication (tous stores)")
        print("3. 🏪 Déclencher publication (store spécifique)")
        print("4. 🔍 Démarrer surveillance automatique")
        print("5. 🛑 Arrêter surveillance automatique")
        print("6. 📊 Statut surveillance")
        print("7. 🏥 Vérifier serveur")
        print("0. ❌ Quitter")
        
        try:
            choice = input("\n👉 Votre choix: ").strip()
            
            if choice == "0":
                print("👋 Au revoir!")
                break
                
            elif choice == "1":
                print("\n📊 Vérification du statut...")
                status = manager.get_poster_media_status()
                manager.display_status(status)
                
            elif choice == "2":
                print("\n🚀 Déclenchement publication (tous stores)...")
                result = manager.trigger_publication()
                manager.display_publication_result(result)
                
            elif choice == "3":
                stores = ["gizmobbs", "logicantiq", "outdoor"]
                print(f"\n🏪 Stores disponibles: {', '.join(stores)}")
                store = input("Store à traiter: ").strip().lower()
                
                if store in stores:
                    print(f"\n🚀 Déclenchement publication pour {store}...")
                    result = manager.trigger_publication(store)
                    manager.display_publication_result(result)
                else:
                    print(f"❌ Store inconnu: {store}")
                    
            elif choice == "4":
                print("\n🔍 Démarrage surveillance automatique...")
                result = manager.start_folder_watcher()
                if result.get("success"):
                    print("✅ Surveillance automatique démarrée!")
                    print("📁 Les fichiers ajoutés aux dossiers seront automatiquement traités")
                else:
                    print(f"❌ Erreur: {result.get('message', 'Erreur inconnue')}")
                    
            elif choice == "5":
                print("\n🛑 Arrêt surveillance automatique...")
                result = manager.stop_folder_watcher()
                if result.get("success"):
                    print("✅ Surveillance automatique arrêtée!")
                else:
                    print(f"❌ Erreur: {result.get('error', 'Erreur inconnue')}")
                    
            elif choice == "6":
                print("\n📊 Vérification statut surveillance...")
                status = manager.get_watcher_status()
                manager.display_watcher_status(status)
                
            elif choice == "7":
                print("\n🏥 Vérification serveur...")
                health = manager.get_server_status()
                if health.get("status") == "ok":
                    print("✅ Serveur opérationnel")
                else:
                    print(f"❌ Problème serveur: {health}")
                    
            else:
                print("❌ Choix invalide")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interruption détectée, au revoir!")
            break
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    main()