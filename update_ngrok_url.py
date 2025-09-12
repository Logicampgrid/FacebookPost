#!/usr/bin/env python3
"""
Mise à jour de l'URL ngrok dans le backend
"""
import requests
import json

def update_ngrok_url():
    """Met à jour l'URL ngrok dans le backend"""
    print("🔄 Mise à jour de l'URL ngrok dans le backend")
    
    try:
        # Récupérer l'URL ngrok
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            tunnels = response.json()
            if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
                ngrok_url = tunnels['tunnels'][0]['public_url']
                print(f"✅ URL ngrok détectée: {ngrok_url}")
                
                # Informer le backend de cette URL
                # On peut créer un endpoint pour cela ou utiliser le système existant
                with open('/app/backend/ngrok_url.txt', 'w') as f:
                    f.write(ngrok_url)
                print(f"💾 URL sauvegardée dans ngrok_url.txt")
                
                # Mettre à jour le .env frontend 
                try:
                    with open('/app/frontend/.env', 'r') as f:
                        lines = f.readlines()
                    
                    updated_lines = []
                    updated = False
                    for line in lines:
                        if line.startswith('REACT_APP_BACKEND_URL='):
                            updated_lines.append(f'REACT_APP_BACKEND_URL={ngrok_url}\n')
                            updated = True
                            print(f"🎯 Frontend .env mis à jour: {ngrok_url}")
                        else:
                            updated_lines.append(line)
                    
                    if not updated:
                        updated_lines.append(f'REACT_APP_BACKEND_URL={ngrok_url}\n')
                        print(f"➕ Frontend .env ligne ajoutée: {ngrok_url}")
                    
                    with open('/app/frontend/.env', 'w') as f:
                        f.writelines(updated_lines)
                        
                except Exception as e:
                    print(f"⚠️ Erreur mise à jour frontend .env: {e}")
                
                return ngrok_url
            else:
                print("❌ Aucun tunnel ngrok trouvé")
                return None
        else:
            print(f"❌ API ngrok non accessible: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

if __name__ == "__main__":
    url = update_ngrok_url()
    if url:
        print(f"\n🎯 URL ngrok mise à jour: {url}")
        print(f"   Maintenant, testez à nouveau l'authentification!")
    else:
        print(f"\n❌ Impossible de mettre à jour l'URL ngrok")