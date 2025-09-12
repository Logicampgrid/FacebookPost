#!/usr/bin/env python3
"""
Script pour vérifier et afficher les sessions ngrok actives
"""
import requests
import subprocess
import json

def check_active_ngrok_sessions():
    """Vérifier les sessions ngrok actives"""
    print("🔍 === VÉRIFICATION SESSIONS NGROK ACTIVES ===")
    
    # Vérifier localement
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            print(f"✅ API ngrok locale accessible: {len(tunnels)} tunnel(s)")
            for tunnel in tunnels:
                print(f"🌐 {tunnel.get('name', 'unnamed')}: {tunnel.get('public_url')} -> {tunnel.get('config', {}).get('addr')}")
            return tunnels
        else:
            print(f"⚠️ API ngrok locale status: {response.status_code}")
    except Exception as e:
        print(f"❌ Pas d'API ngrok locale: {e}")
    
    # Vérifier les processus système
    try:
        if hasattr(subprocess, 'check_output'):
            # Linux/Unix
            result = subprocess.run(['pgrep', '-f', 'ngrok'], capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                print(f"🔍 Processus ngrok détectés: PIDs {pids}")
            else:
                print("ℹ️ Aucun processus ngrok détecté")
    except:
        try:
            # Windows fallback
            result = subprocess.run(['tasklist', '/fi', 'imagename eq ngrok.exe'], 
                                  capture_output=True, text=True)
            if 'ngrok.exe' in result.stdout:
                print("🔍 Processus ngrok.exe détecté sur Windows")
            else:
                print("ℹ️ Aucun processus ngrok.exe sur Windows")
        except:
            print("⚠️ Impossible de vérifier les processus système")
    
    return []

if __name__ == "__main__":
    check_active_ngrok_sessions()