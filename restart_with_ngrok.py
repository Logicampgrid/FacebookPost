#!/usr/bin/env python3
"""
Script pour redémarrer le système avec ngrok
Usage: python3 restart_with_ngrok.py
"""

import subprocess
import time
import requests
import sys

def run_command(cmd, description):
    """Exécute une commande et affiche le résultat"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Succès")
            return True
        else:
            print(f"❌ {description} - Erreur: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def get_ngrok_url():
    """Récupère l'URL ngrok actuelle"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        response.raise_for_status()
        
        tunnels = response.json()
        if tunnels.get('tunnels') and len(tunnels['tunnels']) > 0:
            return tunnels['tunnels'][0]['public_url']
        return None
    except:
        return None

def main():
    print("🚀 Redémarrage du système avec ngrok")
    print("=" * 50)
    
    # 1. Arrêter ngrok existant
    print("🛑 Arrêt des processus ngrok existants...")
    subprocess.run("pkill -f ngrok", shell=True, capture_output=True)
    time.sleep(2)
    
    # 2. Redémarrer le backend
    if not run_command("sudo supervisorctl restart backend", "Redémarrage backend"):
        sys.exit(1)
    
    # 3. Démarrer ngrok
    print("🌐 Démarrage de ngrok...")
    subprocess.Popen("ngrok http 8001 --log=stdout --log-level=info > /tmp/ngrok.log 2>&1", shell=True)
    
    # 4. Attendre que ngrok soit prêt
    print("⏳ Attente de ngrok (15 secondes)...")
    time.sleep(15)
    
    # 5. Vérifier l'URL ngrok
    url = get_ngrok_url()
    if url:
        print(f"✅ Ngrok actif: {url}")
        print(f"🔗 Webhook n8n: {url}/api/webhook/n8n")
        print(f"🔗 Webhook général: {url}/api/webhook")
        
        # 6. Test rapide
        print("🧪 Test rapide du webhook...")
        try:
            response = requests.post(
                f"{url}/api/webhook/n8n",
                json={"test": "restart_check", "message": "Test après redémarrage"},
                timeout=10
            )
            if response.status_code == 200:
                print("✅ Test webhook réussi")
            else:
                print(f"⚠️ Test webhook: HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️ Test webhook échoué: {e}")
        
        print("\n🎉 Système redémarré avec succès !")
        print(f"📋 Utilisez cette URL dans n8n: {url}/api/webhook/n8n")
        
    else:
        print("❌ Impossible de récupérer l'URL ngrok")
        print("🔍 Vérifiez les logs: tail -f /tmp/ngrok.log")
        sys.exit(1)

if __name__ == "__main__":
    main()