#!/usr/bin/env python3
"""
Script pour récupérer l'URL ngrok publique
Usage: python3 get_ngrok_url.py
"""

import requests
import json
import sys

def get_ngrok_url():
    try:
        # Récupérer les tunnels ngrok
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        response.raise_for_status()
        
        tunnels = response.json()
        if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
            public_url = tunnels['tunnels'][0]['public_url']
            return public_url
        else:
            return None
            
    except Exception as e:
        print(f"Erreur lors de la récupération de l'URL ngrok: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    url = get_ngrok_url()
    if url:
        print(f"URL ngrok publique: {url}")
        print(f"Webhook endpoint pour n8n: {url}/api/webhook/n8n")
        print(f"Webhook endpoint général: {url}/api/webhook")
    else:
        print("Aucune URL ngrok trouvée. Vérifiez que ngrok est en cours d'exécution.")
        sys.exit(1)