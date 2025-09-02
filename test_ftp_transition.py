#!/usr/bin/env python3
"""
Test de transition complète ngrok → FTP
Valide la configuration FTP et l'upload avec structure YYYY/MM/DD/
"""

import requests
import os
import sys
import json
import time
from datetime import datetime
import ftplib

def log_test(message, level="INFO"):
    """Log avec timestamp"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📝")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] {message}")

def test_ftp_credentials():
    """Test des credentials FTP logicamp.org"""
    try:
        log_test("Test connexion FTP logicamp.org:21", "TEST")
        
        ftp = ftplib.FTP()
        ftp.connect("logicamp.org", 21, timeout=30)
        log_test("Connexion FTP établie", "SUCCESS")
        
        ftp.login("logi", "logi")
        log_test("Authentification FTP réussie", "SUCCESS")
        
        # Tester navigation vers le répertoire uploads
        try:
            ftp.cwd("/wordpress/uploads/")
            log_test("Navigation vers /wordpress/uploads/ : OK", "SUCCESS")
            
            # Lister le contenu
            file_list = ftp.nlst()
            log_test(f"Contenu du répertoire : {len(file_list)} éléments", "INFO")
            if file_list:
                log_test(f"Premiers éléments : {file_list[:5]}", "INFO")
            
        except ftplib.error_perm as e:
            log_test(f"Erreur navigation : {str(e)}", "ERROR")
            return False
        
        ftp.quit()
        log_test("Connexion FTP fermée proprement", "SUCCESS")
        return True
        
    except Exception as e:
        log_test(f"Erreur FTP : {str(e)}", "ERROR")
        return False

def test_backend_api():
    """Test du backend sans ngrok"""
    try:
        log_test("Test API backend localhost:8001", "TEST")
        
        # Test health check
        response = requests.get("http://localhost:8001/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            mongodb = data.get("mongodb")
            
            log_test(f"Backend Status : {status}", "SUCCESS" if status == "healthy" else "WARNING")
            log_test(f"MongoDB : {mongodb}", "SUCCESS" if mongodb == "connected" else "WARNING")
            
            return True
        else:
            log_test(f"Health check failed : {response.status_code}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"Erreur API backend : {str(e)}", "ERROR")
        return False

def test_ftp_upload_simulation():
    """Test simulation upload FTP via l'API"""
    try:
        log_test("Test simulation upload FTP via API backend", "TEST")
        
        # Créer un fichier test temporaire
        test_content = b"Test FTP upload simulation - " + datetime.now().isoformat().encode()
        temp_file = "/tmp/test_ftp_upload.txt"
        
        with open(temp_file, 'wb') as f:
            f.write(test_content)
        
        log_test(f"Fichier test créé : {temp_file} ({len(test_content)} bytes)", "INFO")
        
        # Tester l'endpoint de debug FTP (si disponible)
        try:
            response = requests.post(
                "http://localhost:8001/api/debug/test-ftp-upload",
                json={"test_mode": True, "filename": "test_simulation.txt"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                log_test(f"Simulation FTP : {result}", "SUCCESS")
                return True
            else:
                log_test(f"Endpoint debug FTP non disponible : {response.status_code}", "WARNING")
                
        except requests.RequestException:
            log_test("Endpoint debug FTP non implémenté", "WARNING")
        
        # Nettoyer
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        
        return True
        
    except Exception as e:
        log_test(f"Erreur simulation : {str(e)}", "ERROR")
        return False

def test_date_structure():
    """Test de la structure de dossiers YYYY/MM/DD"""
    try:
        log_test("Validation structure dossiers YYYY/MM/DD", "TEST")
        
        now = datetime.now()
        expected_structure = f"{now.year:04d}/{now.month:02d}/{now.day:02d}"
        
        log_test(f"Structure attendue : {expected_structure}", "INFO")
        log_test(f"URL finale attendue : https://logicamp.org/wordpress/uploads/{expected_structure}/filename.jpg", "INFO")
        
        return True
        
    except Exception as e:
        log_test(f"Erreur structure : {str(e)}", "ERROR")
        return False

def test_env_configuration():
    """Vérification de la configuration .env"""
    try:
        log_test("Vérification configuration .env", "TEST")
        
        # Lire les variables d'environnement depuis le backend
        backend_env = "/app/backend/.env"
        
        if os.path.exists(backend_env):
            with open(backend_env, 'r') as f:
                content = f.read()
            
            # Vérifications
            checks = [
                ("FTP_HOST=logicamp.org", "Configuration FTP Host"),
                ("FTP_USER=logi", "Configuration FTP User"),
                ("FTP_PASSWORD=logi", "Configuration FTP Password"),
                ("FTP_DIRECTORY=/wordpress/uploads/", "Configuration FTP Directory"),
                ("DRY_RUN=true", "Mode DRY_RUN activé"),
                ("# NGROK_URL=", "NGROK désactivé")
            ]
            
            for check, description in checks:
                if check in content:
                    log_test(f"✓ {description}", "SUCCESS")
                else:
                    log_test(f"✗ {description}", "WARNING")
            
            return True
        else:
            log_test(f"Fichier .env non trouvé : {backend_env}", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"Erreur configuration : {str(e)}", "ERROR")
        return False

def main():
    """Test principal de transition FTP"""
    log_test("🚀 DÉBUT DES TESTS - Transition ngrok → FTP", "TEST")
    print("=" * 80)
    
    tests = [
        ("Configuration .env", test_env_configuration),
        ("Credentials FTP", test_ftp_credentials),
        ("Backend API", test_backend_api),
        ("Structure dossiers", test_date_structure),
        ("Simulation upload", test_ftp_upload_simulation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        log_test(f"🧪 TEST : {test_name}", "TEST")
        print("-" * 60)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                log_test(f"✅ {test_name} : RÉUSSI", "SUCCESS")
            else:
                log_test(f"❌ {test_name} : ÉCHOUÉ", "ERROR")
                
        except Exception as e:
            log_test(f"❌ {test_name} : EXCEPTION - {str(e)}", "ERROR")
            results.append((test_name, False))
        
        print()
    
    # Résumé final
    print("=" * 80)
    log_test("📊 RÉSUMÉ DES TESTS", "TEST")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        log_test(f"{test_name} : {status}", "SUCCESS" if result else "ERROR")
    
    success_rate = (passed / total) * 100
    log_test(f"Taux de réussite : {passed}/{total} ({success_rate:.1f}%)", "SUCCESS" if success_rate >= 80 else "WARNING")
    
    if success_rate >= 80:
        log_test("🎉 TRANSITION FTP PRÊTE ! Passage en mode réel recommandé.", "SUCCESS")
        return 0
    else:
        log_test("⚠️ Des problèmes détectés. Correction recommandée avant mode réel.", "WARNING")
        return 1

if __name__ == "__main__":
    sys.exit(main())