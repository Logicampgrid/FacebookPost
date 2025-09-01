#!/usr/bin/env python3
"""
Exemple d'utilisation de l'API poster_media()
Script client pour déclencher et monitorer la publication automatique Instagram
"""

import requests
import json
import time
import sys

class PosterMediaClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        
    def get_status(self):
        """Récupère le statut et la configuration actuelle"""
        try:
            response = requests.get(f"{self.base_url}/api/poster-media/status")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Erreur lors de la récupération du statut: {e}")
            return None
    
    def trigger_publication(self):
        """Déclenche la publication des médias"""
        try:
            response = requests.post(f"{self.base_url}/api/poster-media")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Erreur lors du déclenchement: {e}")
            return None
    
    def display_status(self, status_data):
        """Affiche le statut de manière formatée"""
        if not status_data:
            return
            
        config = status_data.get("configuration", {})
        analysis = status_data.get("source_analysis", {})
        
        print("📊 STATUT POSTER_MEDIA")
        print("=" * 40)
        print(f"📁 Dossier source: {config.get('source_directory', 'N/A')}")
        print(f"🌍 Serveur FTP: {config.get('ftp_server', 'N/A')}")
        print(f"👤 Utilisateur FTP: {config.get('ftp_user', 'N/A')}")
        print(f"📂 Dossier upload: {config.get('ftp_upload_dir', 'N/A')}")
        print(f"🔑 Token Instagram: {'✅ Configuré' if config.get('access_token_configured') else '❌ Non configuré'}")
        print(f"🆔 User ID Instagram: {'✅ Configuré' if config.get('ig_user_id_configured') else '❌ Non configuré'}")
        print(f"📋 Configuration: {'✅ Valide' if config.get('config_valid') else '❌ Incomplète'}")
        print()
        print(f"📊 ANALYSE DU DOSSIER SOURCE")
        print("=" * 40)
        print(f"📁 Dossier existe: {'✅ Oui' if config.get('source_exists') else '❌ Non'}")
        print(f"📄 Fichiers détectés: {analysis.get('files_count', 0)}")
        print(f"💾 Taille totale: {analysis.get('total_size_mb', 0)} MB")
        print(f"🚀 Prêt à traiter: {'✅ Oui' if status_data.get('ready_to_process') else '❌ Non'}")
        
        # Afficher les fichiers prêts
        files_ready = analysis.get('files_ready', [])
        if files_ready:
            print(f"\n📋 FICHIERS PRÊTS À PUBLIER (aperçu):")
            for file_info in files_ready[:5]:  # Limite à 5 pour l'affichage
                print(f"   • {file_info['filename']} ({file_info['extension']}, {file_info['size_mb']} MB)")
            if len(files_ready) > 5:
                print(f"   ... et {len(files_ready) - 5} autres fichiers")
    
    def display_result(self, result_data):
        """Affiche le résultat de la publication"""
        if not result_data:
            return
            
        result = result_data.get("result", {})
        stats = result.get("stats", {})
        
        print("\n🎯 RÉSULTAT DE LA PUBLICATION")
        print("=" * 40)
        print(f"✅ Succès global: {'Oui' if result_data.get('success') else 'Non'}")
        print(f"⏰ Timestamp: {result_data.get('timestamp', 'N/A')}")
        print(f"📁 Dossier traité: {result_data.get('source_directory', 'N/A')}")
        print(f"📤 Serveur FTP: {result_data.get('ftp_server', 'N/A')}")
        print(f"📱 Compte Instagram: {result_data.get('instagram_account', 'N/A')}")
        
        if stats:
            print(f"\n📊 STATISTIQUES DÉTAILLÉES")
            print("=" * 40)
            print(f"🔍 Fichiers trouvés: {stats.get('files_found', 0)}")
            print(f"⚙️  Fichiers traités: {stats.get('files_processed', 0)}")
            print(f"📤 Fichiers uploadés: {stats.get('files_uploaded', 0)}")
            print(f"📱 Fichiers publiés: {stats.get('files_published', 0)}")
            print(f"⚠️  Fichiers ignorés: {stats.get('files_ignored', 0)}")
            print(f"❌ Fichiers en échec: {stats.get('files_failed', 0)}")
            
            # Afficher les erreurs s'il y en a
            errors = stats.get('errors', [])
            if errors:
                print(f"\n❌ ERREURS DÉTAILLÉES:")
                for error in errors:
                    print(f"   • {error}")
        
        message = result.get('message', result.get('error', 'Aucun message'))
        print(f"\n💬 Message: {message}")

def main():
    """Fonction principale - exemple d'utilisation"""
    
    print("🚀 Client PosterMedia - Publication automatique Instagram")
    print("=" * 60)
    
    client = PosterMediaClient()
    
    # Étape 1: Vérifier le statut
    print("1️⃣ Vérification du statut et de la configuration...")
    status = client.get_status()
    
    if status:
        client.display_status(status)
        
        # Vérifier si on peut procéder
        if status.get("ready_to_process", False):
            print("\n✅ Configuration valide et fichiers détectés!")
            
            # Demander confirmation
            try:
                confirm = input(f"\nVoulez-vous déclencher la publication de {status['source_analysis']['files_count']} fichiers ? (o/N): ")
                if confirm.lower() in ['o', 'oui', 'y', 'yes']:
                    print("\n2️⃣ Déclenchement de la publication...")
                    result = client.trigger_publication()
                    client.display_result(result)
                else:
                    print("❌ Publication annulée par l'utilisateur")
            except KeyboardInterrupt:
                print("\n❌ Opération interrompue par l'utilisateur")
        else:
            print("\n⚠️  Configuration incomplète ou aucun fichier détecté")
            print("📋 Actions requises:")
            
            config = status.get("configuration", {})
            if not config.get("source_exists"):
                print(f"   • Créer le dossier: {config.get('source_directory')}")
            if not config.get("access_token_configured"):
                print("   • Configurer ACCESS_TOKEN dans le fichier .env")
            if not config.get("ig_user_id_configured"):
                print("   • Configurer IG_USER_ID dans le fichier .env")
            if status.get("source_analysis", {}).get("files_count", 0) == 0:
                print("   • Placer des fichiers images/vidéos dans le dossier source")
    else:
        print("❌ Impossible de récupérer le statut du serveur")
        print("Vérifiez que le serveur FastAPI est démarré sur http://localhost:8001")

if __name__ == "__main__":
    main()