import os
import requests
import sys

# Ajouter le chemin vers le backend pour importer les fonctions existantes
sys.path.insert(0, os.path.dirname(__file__))

try:
    from server import get_active_ngrok_url, UPLOAD_DIR, FACEBOOK_GRAPH_URL, STORES, get_store_config, PUBLICATION_TEST_MODE
    INTEGRATION_AVAILABLE = True
except ImportError:
    print("[⚠️] Impossible d'importer les modules du serveur - mode autonome")
    INTEGRATION_AVAILABLE = False
    UPLOAD_DIR = "uploads"
    FACEBOOK_GRAPH_URL = "https://graph.facebook.com/v17.0"

# === CONFIGURATION ===
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")  # ton token Instagram
NGROK_URL = os.getenv("NGROK_URL", "http://localhost:8001")  # ton URL ngrok (fallback)
UPLOAD_FOLDER = UPLOAD_DIR  # utiliser la configuration du serveur
CAPTION = "Découvrez notre boutique !"

# === FONCTIONS AMÉLIORÉES ===
def get_backend_url() -> str:
    """
    Récupère l'URL backend active (priorité au système du serveur)
    """
    if INTEGRATION_AVAILABLE:
        try:
            return get_active_ngrok_url() or NGROK_URL
        except:
            pass
    return NGROK_URL

def to_public_url(local_path: str) -> str:
    """
    Convertit un fichier local du dossier uploads/ en URL publique pour Instagram.
    """
    filename = os.path.basename(local_path)
    backend_url = get_backend_url()
    return f"{backend_url}/{UPLOAD_FOLDER}/{filename}"

def post_to_instagram(image_url: str, caption: str, access_token: str = None, ig_user_id: str = None):
    """
    Poste l'image sur Instagram en utilisant l'API Graph.
    """
    token = access_token or ACCESS_TOKEN
    if not token:
        print("[⚠️] Token d'accès Instagram manquant")
        return False
    
    # Si intégré au serveur et ig_user_id non fourni, essayer de le récupérer
    if INTEGRATION_AVAILABLE and not ig_user_id:
        try:
            # Utiliser le premier store disponible avec Instagram
            for store_key, store_config in STORES.items():
                config = get_store_config(store_key)
                if config.get("ig_user_id") and config.get("access_token"):
                    ig_user_id = config["ig_user_id"]
                    token = config["access_token"]  # Utiliser le token du store
                    print(f"[ℹ️] Utilisation du store {store_key} (IG: {ig_user_id})")
                    break
        except:
            pass
    
    if not ig_user_id:
        print("[⚠️] ID utilisateur Instagram manquant")
        return False
    
    # Mode test si disponible
    if INTEGRATION_AVAILABLE and PUBLICATION_TEST_MODE:
        print(f"[🧪] MODE TEST - Publication simulée: {image_url}")
        return True
    
    try:
        # Étape 1: Créer le conteneur média
        endpoint = f"{FACEBOOK_GRAPH_URL}/{ig_user_id}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": token
        }
        response = requests.post(endpoint, data=payload, timeout=30)
        
        if response.status_code == 200:
            creation_id = response.json().get("id")
            
            if creation_id:
                # Étape 2: Publier le média
                publish_endpoint = f"{FACEBOOK_GRAPH_URL}/{ig_user_id}/media_publish"
                publish_payload = {
                    "creation_id": creation_id,
                    "access_token": token
                }
                publish_response = requests.post(publish_endpoint, data=publish_payload, timeout=30)
                
                if publish_response.status_code == 200:
                    instagram_id = publish_response.json().get("id")
                    print(f"[✅] Image publiée : {image_url} (ID: {instagram_id})")
                    return True
                else:
                    print(f"[⚠️] Erreur publication : {publish_response.text}")
            else:
                print("[⚠️] ID de création manquant dans la réponse")
        else:
            print(f"[⚠️] Erreur création média : {response.text}")
    except Exception as e:
        print(f"[❌] Erreur lors de la publication : {str(e)}")
    
    return False

# === BOUCLE SUR TOUS LES FICHIERS ===
def main(store_name: str = None, custom_caption: str = None):
    """
    Fonction principale avec support optionnel pour store spécifique
    """
    print(f"[🚀] Démarrage publication en masse Instagram")
    print(f"[ℹ️] Backend URL: {get_backend_url()}")
    print(f"[ℹ️] Upload folder: {UPLOAD_FOLDER}")
    print(f"[ℹ️] Intégration serveur: {'✅' if INTEGRATION_AVAILABLE else '❌'}")
    
    if not os.path.exists(UPLOAD_FOLDER):
        print(f"[⚠️] Dossier {UPLOAD_FOLDER} introuvable.")
        return False
    
    # Filtrer les fichiers image
    supported_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    image_files = []
    
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename.lower())
            if ext in supported_extensions:
                image_files.append(file_path)
    
    if not image_files:
        print(f"[⚠️] Aucun fichier image trouvé dans {UPLOAD_FOLDER}.")
        print(f"[ℹ️] Extensions supportées: {', '.join(supported_extensions)}")
        return False
    
    print(f"[📸] {len(image_files)} fichiers image trouvés")
    
    # Configuration pour publication
    caption = custom_caption or CAPTION
    access_token = None
    ig_user_id = None
    
    # Si intégré au serveur et store spécifié
    if INTEGRATION_AVAILABLE and store_name:
        try:
            if store_name in STORES:
                config = get_store_config(store_name)
                access_token = config.get("access_token")
                ig_user_id = config.get("ig_user_id")
                print(f"[ℹ️] Utilisation du store: {config.get('name', store_name)}")
            else:
                print(f"[⚠️] Store '{store_name}' inconnu")
                return False
        except Exception as e:
            print(f"[⚠️] Erreur configuration store: {e}")
            return False
    
    # Publication de chaque fichier
    success_count = 0
    for file_path in image_files:
        public_url = to_public_url(file_path)
        print(f"[📤] Publication: {os.path.basename(file_path)} -> {public_url}")
        
        if post_to_instagram(public_url, caption, access_token, ig_user_id):
            success_count += 1
            # Pause entre publications
            import time
            time.sleep(2)
    
    total_files = len(image_files)
    print(f"[📊] Publication terminée: {success_count}/{total_files} réussies")
    
    return success_count == total_files

if __name__ == "__main__":
    # Paramètres optionnels depuis la ligne de commande
    import sys
    
    store_name = None
    custom_caption = None
    
    if len(sys.argv) > 1:
        store_name = sys.argv[1]
    if len(sys.argv) > 2:
        custom_caption = sys.argv[2]
    
    success = main(store_name, custom_caption)
    sys.exit(0 if success else 1)