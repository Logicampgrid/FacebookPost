#!/usr/bin/env python3
"""
Script de diagnostic ngrok pour tester la connectivité
"""
import subprocess
import requests
import time
import os

def test_ngrok_standalone():
    """Test ngrok en mode standalone pour diagnostic"""
    print("🔍 === DIAGNOSTIC NGROK ===")
    
    # Test 1: Vérifier si ngrok est installé
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Ngrok installé: {result.stdout.strip()}")
        else:
            print(f"❌ Erreur ngrok version: {result.stderr}")
            return
    except Exception as e:
        print(f"❌ Ngrok non trouvé: {e}")
        return
    
    # Test 2: Vérifier la configuration
    ngrok_token = os.getenv("NGROK_AUTH_TOKEN", "30KVU5Oxya5afdPt46syFR1KD65_3kxesHED2kbcHpDNW6VhT")
    if ngrok_token:
        try:
            subprocess.run(["ngrok", "config", "add-authtoken", ngrok_token], 
                         capture_output=True, check=True)
            print("✅ Token ngrok configuré")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Erreur configuration token: {e}")
    
    # Test 3: Essayer de lancer ngrok
    print("🚀 Lancement test ngrok sur port 8001...")
    
    try:
        process = subprocess.Popen([
            "ngrok", "http", "8001", "--log=stdout"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print(f"✅ Processus ngrok lancé (PID: {process.pid})")
        
        # Attendre 10 secondes
        for i in range(10):
            time.sleep(1)
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                print(f"❌ Processus ngrok arrêté après {i+1}s")
                print(f"STDOUT: {stdout[:500]}")
                print(f"STDERR: {stderr[:500]}")
                return
            else:
                print(f"⏳ Ngrok actif ({i+1}s/10s)")
        
        # Test de l'API
        print("🔍 Test de l'API ngrok...")
        for attempt in range(5):
            try:
                response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ API ngrok accessible: {len(data.get('tunnels', []))} tunnel(s)")
                    for tunnel in data.get('tunnels', []):
                        print(f"🌐 Tunnel: {tunnel.get('public_url')}")
                    break
                else:
                    print(f"⚠️ API ngrok status: {response.status_code}")
            except Exception as e:
                print(f"⏳ Tentative {attempt+1}/5: {e}")
                time.sleep(2)
        
        # Nettoyage
        print("🛑 Arrêt du processus test...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except:
            process.kill()
            
    except Exception as e:
        print(f"❌ Erreur lancement ngrok: {e}")

if __name__ == "__main__":
    test_ngrok_standalone()