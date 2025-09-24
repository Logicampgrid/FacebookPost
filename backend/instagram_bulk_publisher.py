import os
import requests

# === CONFIGURATION ===
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")  # ton token Instagram
NGROK_URL = os.getenv("NGROK_URL", "http://localhost:8001")  # ton URL ngrok
UPLOAD_FOLDER = "uploads"  # dossier contenant les fichiers locaux
CAPTION = "Découvrez notre boutique !"

# === FONCTIONS ===
def to_public_url(local_path: str) -> str:
    """
    Convertit un fichier local du dossier uploads/ en URL publique pour Instagram via ngrok.
    """
    filename = os.path.basename(local_path)
    return f"{NGROK_URL}/{UPLOAD_FOLDER}/{filename}"

def post_to_instagram(image_url: str, caption: str):
    """
    Poste l'image sur Instagram en utilisant l'API Graph.
    """
    endpoint = "https://graph.facebook.com/v17.0/me/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    response = requests.post(endpoint, data=payload)
    if response.status_code == 200:
        creation_id = response.json().get("id")
        # Publier le média
        publish_endpoint = f"https://graph.facebook.com/v17.0/me/media_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": ACCESS_TOKEN
        }
        publish_response = requests.post(publish_endpoint, data=publish_payload)
        if publish_response.status_code == 200:
            print(f"[✅] Image publiée : {image_url}")
        else:
            print(f"[⚠️] Erreur publication : {publish_response.text}")
    else:
        print(f"[⚠️] Erreur création média : {response.text}")

# === BOUCLE SUR TOUS LES FICHIERS ===
def main():
    if not os.path.exists(UPLOAD_FOLDER):
        print(f"[⚠️] Dossier {UPLOAD_FOLDER} introuvable.")
        return

    local_files = [os.path.join(UPLOAD_FOLDER, f) for f in os.listdir(UPLOAD_FOLDER)
                   if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]

    if not local_files:
        print(f"[⚠️] Aucun fichier dans {UPLOAD_FOLDER}.")
        return

    for file_path in local_files:
        public_url = to_public_url(file_path)
        post_to_instagram(public_url, CAPTION)

if __name__ == "__main__":
    main()