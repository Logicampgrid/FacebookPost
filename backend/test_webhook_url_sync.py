#!/usr/bin/env python3
"""
Test et correction automatique WEBHOOK_URL après redémarrage ngrok
"""

import os
import time
import requests
from dotenv import load_dotenv

def get_current_webhook_url():
    """Récupère WEBHOOK_URL actuel du .env"""
    load_dotenv()
    return os.getenv("WEBHOOK_URL")

def get_active_ngrok_url():
    """Récupère l'URL ngrok active"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            for tunnel in tunnels:
                if tunnel.get('config', {}).get('addr') == "http://localhost:8001":
                    return tunnel.get('public_url')
            # Si pas de tunnel spécifique, prendre le premier
            if tunnels:
                return tunnels[0].get('public_url')
    except:
        pass
    return None

def update_webhook_url_in_env(new_url):
    """Met à jour WEBHOOK_URL dans le .env backend"""
    env_path = "/app/backend/.env"
    
    # Lire le fichier actuel
    with open(env_path, "r", encoding='utf-8') as f:
        lines = f.readlines()
    
    # Mettre à jour la ligne WEBHOOK_URL
    updated_lines = []
    url_updated = False
    
    for line in lines:
        if line.startswith("WEBHOOK_URL="):
            old_url = line.split("=", 1)[1].strip() if "=" in line else ""
            updated_lines.append(f"WEBHOOK_URL={new_url}\n")
            print(f"✅ WEBHOOK_URL mis à jour: {old_url} -> {new_url}")
            url_updated = True
        else:
            updated_lines.append(line)
    
    if not url_updated:
        updated_lines.append(f"WEBHOOK_URL={new_url}\n")
        print(f"✅ WEBHOOK_URL ajouté: {new_url}")
    
    # Réécrire le fichier
    with open(env_path, "w", encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    return True

def update_frontend_env(new_url):
    """Met à jour REACT_APP_BACKEND_URL dans le frontend .env"""
    frontend_env_path = "/app/frontend/.env"
    
    if not os.path.exists(frontend_env_path):
        print(f"⚠️ Frontend .env non trouvé: {frontend_env_path}")
        return False
    
    # Lire le fichier actuel
    with open(frontend_env_path, "r", encoding='utf-8') as f:
        lines = f.readlines()
    
    # Mettre à jour la ligne REACT_APP_BACKEND_URL
    updated_lines = []
    url_updated = False
    
    for line in lines:
        if line.startswith("REACT_APP_BACKEND_URL="):
            old_url = line.split("=", 1)[1].strip() if "=" in line else ""
            updated_lines.append(f"REACT_APP_BACKEND_URL={new_url}\n")
            print(f"✅ REACT_APP_BACKEND_URL mis à jour: {old_url} -> {new_url}")
            url_updated = True
        else:
            updated_lines.append(line)
    
    if not url_updated:
        updated_lines.append(f"REACT_APP_BACKEND_URL={new_url}\n")
        print(f"✅ REACT_APP_BACKEND_URL ajouté: {new_url}")
    
    # Réécrire le fichier
    with open(frontend_env_path, "w", encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    return True

def test_webhook_url_sync():
    """Test la synchronisation automatique de WEBHOOK_URL"""
    print("🔧 Test synchronisation automatique WEBHOOK_URL")
    print("=" * 50)
    
    # 1. Vérifier l'URL actuelle
    current_webhook_url = get_current_webhook_url()
    print(f"📋 WEBHOOK_URL actuel: {current_webhook_url}")
    
    # 2. Détecter ngrok actif
    ngrok_url = get_active_ngrok_url()
    print(f"🔍 Ngrok détecté: {ngrok_url}")
    
    if not ngrok_url:
        print("⚠️ Aucun tunnel ngrok actif - Simulation avec URL de test")
        ngrok_url = "https://test-webhook-sync.ngrok-free.app"
    
    # 3. Comparer et mettre à jour si nécessaire
    if current_webhook_url != ngrok_url:
        print(f"🔄 Synchronisation nécessaire: {current_webhook_url} -> {ngrok_url}")
        
        # Mettre à jour backend .env
        if update_webhook_url_in_env(ngrok_url):
            print("✅ Backend .env mis à jour")
        
        # Mettre à jour frontend .env
        if update_frontend_env(ngrok_url):
            print("✅ Frontend .env mis à jour")
        
        print("🎯 Synchronisation terminée !")
        return True
    else:
        print("✅ WEBHOOK_URL déjà synchronisé - Aucune action nécessaire")
        return True

def test_webhook_accessibility():
    """Test l'accessibilité de la route webhook"""
    webhook_url = get_current_webhook_url()
    if not webhook_url:
        print("❌ Aucune WEBHOOK_URL configurée")
        return False
    
    test_url = f"{webhook_url}/api/webhook"
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "mon_token_secret_webhook",
        "hub.challenge": "sync_test_12345"
    }
    
    try:
        response = requests.get(test_url, params=params, timeout=10)
        if response.status_code == 200 and response.text == "sync_test_12345":
            print(f"✅ Webhook accessible: {test_url}")
            return True
        else:
            print(f"❌ Webhook non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur test webhook: {e}")
        return False

def main():
    """Test complet de synchronisation WEBHOOK_URL"""
    print("🚀 Test automatique synchronisation WEBHOOK_URL")
    print("📝 Rappel: Après redémarrage ngrok, exécuter ce script pour mettre à jour .env")
    print("=" * 70)
    
    # Test 1: Synchronisation
    sync_success = test_webhook_url_sync()
    
    print("\n" + "=" * 50)
    
    # Test 2: Accessibilité
    access_success = test_webhook_accessibility()
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS")
    print("=" * 50)
    print(f"Synchronisation: {'✅ OK' if sync_success else '❌ ÉCHEC'}")
    print(f"Accessibilité:   {'✅ OK' if access_success else '❌ ÉCHEC'}")
    
    if sync_success and access_success:
        print("\n🎉 WEBHOOK_URL correctement synchronisé et accessible !")
        print("💡 RAPPEL: Mettre à jour WEBHOOK_URL dans .env après chaque redémarrage ngrok")
    else:
        print("\n⚠️ Problèmes détectés - Vérifiez la configuration ngrok")
        
    return sync_success and access_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)