#!/usr/bin/env python3
"""
Test de l'accessibilité HTTP des URLs FTP générées
"""

import requests
import time
from datetime import datetime

def log_test(message: str, level: str = "INFO"):
    """Logging pour les tests"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [HTTP TEST] {message}")

def test_existing_urls():
    """Test des URLs d'exemple des logs"""
    
    # URLs des logs fournis qui échouent
    test_urls = [
        "https://logicamp.org/wordpress/uploads/webhook_70e3eb71_1759961667.png",
        "https://logicamp.org/wordpress/uploads/webhook_6c869b96_1759961719.jpg", 
        "https://logicamp.org/wordpress/uploads/webhook_26373262_1759961765.png",
        "https://logicamp.org/wordpress/uploads/webhook_c094f026_1759961813.mp4",
    ]
    
    log_test("🧪 Test d'accessibilité HTTP des URLs FTP générées", "INFO")
    
    for url in test_urls:
        try:
            log_test(f"Test: {url}", "INFO")
            
            response = requests.get(url, timeout=10, allow_redirects=True)
            
            log_test(f"Status: {response.status_code}", "INFO")
            log_test(f"Content-Type: {response.headers.get('content-type', 'N/A')}", "INFO")
            log_test(f"Content-Length: {response.headers.get('content-length', 'N/A')}", "INFO")
            
            if response.status_code == 200:
                log_test(f"✅ SUCCÈS - Fichier accessible", "SUCCESS")
            elif response.status_code == 404:
                log_test(f"❌ ÉCHEC - 404 Not Found", "ERROR")
            else:
                log_test(f"⚠️ Status inattendu: {response.status_code}", "WARNING")
                
        except requests.exceptions.Timeout:
            log_test(f"❌ TIMEOUT - Serveur ne répond pas", "ERROR")
        except requests.exceptions.ConnectionError:
            log_test(f"❌ CONNECTION ERROR - Impossible de se connecter", "ERROR")
        except Exception as e:
            log_test(f"❌ ERREUR: {e}", "ERROR")
        
        print()  # Ligne vide pour clarté

def test_base_paths():
    """Test des chemins de base pour voir s'ils sont accessibles"""
    
    base_urls = [
        "https://logicamp.org/",
        "https://logicamp.org/wordpress/",
        "https://logicamp.org/wordpress/uploads/",
        "https://www.logicamp.org/",
        "https://www.logicamp.org/wordpress/",
        "https://www.logicamp.org/wordpress/uploads/",
    ]
    
    log_test("🔍 Test des chemins de base:", "INFO")
    
    for base_url in base_urls:
        try:
            log_test(f"Test: {base_url}", "INFO")
            
            response = requests.get(base_url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                log_test(f"✅ ACCESSIBLE - {response.status_code}", "SUCCESS")
            elif response.status_code in [301, 302]:
                log_test(f"🔄 REDIRECT - {response.status_code} vers {response.headers.get('location', 'N/A')}", "INFO")
            else:
                log_test(f"❌ ÉCHEC - {response.status_code}", "WARNING")
                
        except Exception as e:
            log_test(f"❌ ERREUR: {e}", "ERROR")
        
        print()

if __name__ == "__main__":
    print("=" * 60)
    print("TEST HTTP ACCESSIBILITY - URLs FTP")
    print("=" * 60)
    
    test_existing_urls()
    
    print("\n" + "=" * 60)
    print("TEST CHEMINS DE BASE")
    print("=" * 60)
    
    test_base_paths()
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    
    print("🔍 Ce test permet d'identifier si le problème vient de:")
    print("   1. URLs complètement inaccessibles (serveur down)")
    print("   2. Chemin incorrect dans l'URL")
    print("   3. Fichiers pas uploadés correctement")
    print("   4. Configuration WordPress/serveur web incorrecte")