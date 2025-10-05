#!/usr/bin/env python3
"""
PATCH 33: Test et validation FTP avec nouveau chemin
Teste l'upload FTP vers /www/wordpress/uploads/ et valide les URLs générées
"""

import os
import sys
import time
import tempfile
import requests
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire backend au path
sys.path.append('/app/backend')

# Import du gestionnaire FTP
try:
    from ftp_manager_patch29 import init_ftp_manager, upload_for_publication, get_ftp_public_url
    FTP_AVAILABLE = True
except ImportError as e:
    print(f"❌ Gestionnaire FTP non disponible: {e}")
    FTP_AVAILABLE = False

def log_test(message: str, level: str = "INFO"):
    """Logging pour les tests"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [TEST PATCH 33] {message}")

def create_test_image() -> str:
    """Crée une image de test"""
    try:
        # Créer un fichier image simple de test
        test_content = b"PATCH 33 Test Image - " + str(time.time()).encode()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg', prefix='test_patch33_') as f:
            f.write(test_content)
            test_file_path = f.name
        
        log_test(f"Image de test créée: {test_file_path}", "SUCCESS")
        return test_file_path
        
    except Exception as e:
        log_test(f"Erreur création image test: {e}", "ERROR")
        return None

def test_ftp_connection():
    """Teste la connexion FTP de base"""
    log_test("=== TEST CONNEXION FTP ===", "TEST")
    
    if not FTP_AVAILABLE:
        log_test("Gestionnaire FTP non disponible", "ERROR")
        return False
    
    try:
        manager = init_ftp_manager()
        log_test(f"Gestionnaire FTP initialisé:", "INFO")
        log_test(f"  - Host: {manager.host}:{manager.port}", "INFO")
        log_test(f"  - User: {manager.user}", "INFO") 
        log_test(f"  - Directory: {manager.base_dir}", "INFO")
        log_test(f"  - Base URL: {manager.base_url}", "INFO")
        
        # Test de connexion
        if manager.test_connection():
            log_test("Connexion FTP réussie!", "SUCCESS")
            return True
        else:
            log_test("Connexion FTP échouée!", "ERROR")
            return False
            
    except Exception as e:
        log_test(f"Erreur test connexion: {e}", "ERROR")
        return False

def test_ftp_upload():
    """Teste l'upload d'un fichier vers FTP"""
    log_test("=== TEST UPLOAD FTP ===", "TEST")
    
    if not FTP_AVAILABLE:
        log_test("Gestionnaire FTP non disponible", "ERROR")
        return False, None
    
    # Créer un fichier de test
    test_file = create_test_image()
    if not test_file:
        log_test("Impossible de créer le fichier de test", "ERROR")
        return False, None
    
    try:
        # Générer un nom de fichier unique
        timestamp = int(time.time())
        filename = f"test_patch33_{timestamp}.jpg"
        
        log_test(f"Upload en cours: {filename}", "INFO")
        
        # Tester l'upload
        success, ftp_url, error = upload_for_publication(test_file, filename)
        
        # Nettoyer le fichier temporaire
        try:
            os.unlink(test_file)
        except:
            pass
            
        if success and ftp_url:
            log_test(f"Upload FTP réussi!", "SUCCESS")
            log_test(f"URL générée: {ftp_url}", "SUCCESS")
            return True, ftp_url
        else:
            log_test(f"Upload FTP échoué: {error}", "ERROR")
            return False, None
            
    except Exception as e:
        log_test(f"Erreur générale upload: {e}", "ERROR")
        # Nettoyer le fichier temporaire
        try:
            os.unlink(test_file)
        except:
            pass
        return False, None

def test_url_accessibility(url: str):
    """Teste si l'URL générée est accessible publiquement"""
    log_test("=== TEST ACCESSIBILITÉ URL ===", "TEST")
    
    if not url:
        log_test("Aucune URL à tester", "WARNING")
        return False
        
    try:
        log_test(f"Test accessibilité: {url}", "INFO")
        
        # Test avec timeout court
        response = requests.head(url, timeout=10, allow_redirects=True)
        
        log_test(f"Réponse HTTP: {response.status_code}", "INFO")
        
        if response.status_code == 200:
            log_test("URL accessible publiquement! ✅", "SUCCESS")
            
            # Tester aussi avec GET pour vérifier le contenu
            try:
                get_response = requests.get(url, timeout=5)
                content_length = len(get_response.content)
                log_test(f"Contenu téléchargé: {content_length} bytes", "SUCCESS")
                return True
            except Exception as get_error:
                log_test(f"Erreur GET (mais HEAD OK): {get_error}", "WARNING")
                return True  # HEAD OK donc considéré comme accessible
                
        elif response.status_code == 404:
            log_test("❌ URL non trouvée (404) - Problème chemin FTP!", "ERROR")
            return False
        else:
            log_test(f"URL non accessible - Status: {response.status_code}", "ERROR")
            return False
            
    except requests.exceptions.Timeout:
        log_test("Timeout - URL potentiellement inaccessible", "WARNING")
        return False
    except requests.exceptions.ConnectionError:
        log_test("Erreur connexion - Serveur non accessible", "ERROR")
        return False
    except Exception as e:
        log_test(f"Erreur test URL: {e}", "ERROR")
        return False

def test_performance():
    """Teste les performances d'upload"""
    log_test("=== TEST PERFORMANCE ===", "TEST")
    
    if not FTP_AVAILABLE:
        log_test("Gestionnaire FTP non disponible", "ERROR")
        return
    
    # Créer plusieurs fichiers de tailles différentes
    test_sizes = [1024, 10240, 51200]  # 1KB, 10KB, 50KB
    
    for size in test_sizes:
        try:
            # Créer fichier de test
            test_content = b'x' * size
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
                f.write(test_content)
                test_file = f.name
            
            filename = f"perf_test_{size}bytes_{int(time.time())}.jpg"
            
            # Mesurer le temps d'upload
            start_time = time.time()
            success, url, error = upload_for_publication(test_file, filename)
            upload_time = time.time() - start_time
            
            # Nettoyer
            try:
                os.unlink(test_file)
            except:
                pass
            
            if success:
                speed_kbps = (size / 1024) / upload_time if upload_time > 0 else 0
                log_test(f"Upload {size} bytes: {upload_time:.2f}s ({speed_kbps:.1f} KB/s)", "SUCCESS")
            else:
                log_test(f"Upload {size} bytes échoué: {error}", "ERROR")
                
        except Exception as e:
            log_test(f"Erreur test performance {size} bytes: {e}", "ERROR")

def main():
    """Fonction principale de test"""
    log_test("🚀 DÉMARRAGE TESTS FTP PATCH 33", "TEST")
    log_test("Objectif: Valider upload FTP vers /www/wordpress/uploads/", "INFO")
    
    results = {
        "connection": False,
        "upload": False, 
        "accessibility": False,
        "url": None
    }
    
    # Test 1: Connexion FTP
    results["connection"] = test_ftp_connection()
    
    if not results["connection"]:
        log_test("❌ Tests interrompus - connexion FTP échoue", "ERROR")
        return results
    
    # Test 2: Upload d'un fichier
    results["upload"], results["url"] = test_ftp_upload()
    
    if not results["upload"]:
        log_test("❌ Tests interrompus - upload FTP échoue", "ERROR")
        return results
    
    # Test 3: Accessibilité de l'URL
    results["accessibility"] = test_url_accessibility(results["url"])
    
    # Test 4: Performance (optionnel)
    test_performance()
    
    # Résumé final
    log_test("=== RÉSUMÉ TESTS PATCH 33 ===", "TEST")
    log_test(f"✅ Connexion FTP: {'OK' if results['connection'] else 'ÉCHEC'}", "SUCCESS" if results["connection"] else "ERROR")
    log_test(f"✅ Upload FTP: {'OK' if results['upload'] else 'ÉCHEC'}", "SUCCESS" if results["upload"] else "ERROR")
    log_test(f"✅ URL accessible: {'OK' if results['accessibility'] else 'ÉCHEC'}", "SUCCESS" if results["accessibility"] else "ERROR")
    
    if results["url"]:
        log_test(f"🔗 URL testée: {results['url']}", "INFO")
    
    # Verdict final
    if all([results["connection"], results["upload"], results["accessibility"]]):
        log_test("🎉 PATCH 33: FTP 100% OPÉRATIONNEL!", "SUCCESS")
        log_test("✅ Le problème d'upload FTP est résolu", "SUCCESS")
    else:
        log_test("⚠️ PATCH 33: Problèmes détectés", "WARNING")
        if not results["accessibility"]:
            log_test("❌ URLs FTP non accessibles - Vérifiez le chemin sur le serveur", "ERROR")
    
    return results

if __name__ == "__main__":
    main()