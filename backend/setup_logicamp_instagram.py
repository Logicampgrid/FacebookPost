#!/usr/bin/env python3
"""
PATCH 47 - Configuration automatique du store Logicamp
Récupère l'Instagram Business Account ID lié à la page Facebook Logicamp
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

FACEBOOK_GRAPH_URL = "https://graph.facebook.com/v18.0"
LOGICAMP_PAGE_ID = "174450429258625"
ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN_LOGICAMP")

def get_instagram_account_id(page_id: str, access_token: str):
    """Récupère l'Instagram Business Account ID lié à une page Facebook"""
    try:
        print(f"🔍 Récupération Instagram ID pour page {page_id}...")
        
        url = f"{FACEBOOK_GRAPH_URL}/{page_id}"
        params = {
            "fields": "instagram_business_account",
            "access_token": access_token
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return None
        
        data = response.json()
        
        if "instagram_business_account" in data:
            ig_id = data["instagram_business_account"]["id"]
            print(f"✅ Instagram Business Account trouvé: {ig_id}")
            return ig_id
        else:
            print(f"⚠️ Pas de compte Instagram lié à cette page")
            print(f"📋 Réponse: {data}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def update_env_file(ig_id: str):
    """Met à jour le fichier .env avec l'Instagram ID"""
    try:
        env_path = "/app/backend/.env"
        
        # Lire le fichier
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Remplacer la ligne IG_USER_ID_LOGICAMP
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("IG_USER_ID_LOGICAMP="):
                lines[i] = f"IG_USER_ID_LOGICAMP={ig_id}\n"
                updated = True
                break
        
        # Écrire le fichier
        if updated:
            with open(env_path, 'w') as f:
                f.writelines(lines)
            print(f"✅ Fichier .env mis à jour avec IG_USER_ID_LOGICAMP={ig_id}")
            return True
        else:
            print(f"⚠️ Variable IG_USER_ID_LOGICAMP non trouvée dans .env")
            return False
            
    except Exception as e:
        print(f"❌ Erreur mise à jour .env: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 PATCH 47 - Configuration Store Logicamp")
    print("=" * 60)
    
    if not ACCESS_TOKEN:
        print("❌ FB_ACCESS_TOKEN_LOGICAMP non trouvé dans .env")
        return
    
    print(f"📋 Page Facebook Logicamp: {LOGICAMP_PAGE_ID}")
    print(f"🔑 Token configuré: {ACCESS_TOKEN[:20]}...")
    print()
    
    # Récupérer l'Instagram ID
    ig_id = get_instagram_account_id(LOGICAMP_PAGE_ID, ACCESS_TOKEN)
    
    if ig_id:
        # Mettre à jour le .env
        if update_env_file(ig_id):
            print()
            print("=" * 60)
            print("✅ CONFIGURATION TERMINÉE")
            print("=" * 60)
            print(f"📋 Store: logicamp")
            print(f"📘 Page Facebook: {LOGICAMP_PAGE_ID}")
            print(f"📸 Instagram: {ig_id}")
            print(f"🔑 Token: Configuré (partagé avec gizmobbs)")
            print()
            print("🔄 Redémarrez le serveur pour appliquer les changements:")
            print("   sudo supervisorctl restart backend")
        else:
            print("⚠️ Configuration réussie mais mise à jour .env échouée")
    else:
        print()
        print("❌ Impossible de récupérer l'Instagram ID")
        print("💡 Vérifiez que la page Logicamp a un compte Instagram lié")

if __name__ == "__main__":
    main()
