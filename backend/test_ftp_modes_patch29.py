#!/usr/bin/env python3
"""
PATCH 29: Test de différents modes FTP
Teste les modes passif/actif avec les nouveaux credentials
"""

import ftplib
import os
import time
from datetime import datetime
from io import BytesIO

# Configuration FTP PATCH 29
FTP_HOST = "logicamp.org"
FTP_PORT = 21
FTP_USER = "logi"
FTP_PASSWORD = "6837"
FTP_DIRECTORY = "/wordpress/uploads/"

def log_test(message: str, level: str = "INFO"):
    """Logging pour les tests"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [FTP TEST] {message}")

def test_ftp_mode(passive_mode: bool, timeout: int = 15):
    """Test d'un mode FTP spécifique"""
    mode_name = "PASSIF" if passive_mode else "ACTIF"
    log_test(f"=== TEST MODE {mode_name} (timeout: {timeout}s) ===", "INFO")
    
    try:
        # Connexion
        ftp = ftplib.FTP()
        ftp.set_pasv(passive_mode)
        ftp.connect(FTP_HOST, FTP_PORT, timeout=timeout)
        log_test(f"✅ Connexion {mode_name} établie", "SUCCESS")
        
        # Authentification
        ftp.login(FTP_USER, FTP_PASSWORD)
        log_test(f"✅ Authentification {mode_name} réussie", "SUCCESS")
        
        # Navigation
        current_dir = ftp.pwd()
        log_test(f"Répertoire: {current_dir}", "INFO")
        
        try:
            ftp.cwd(FTP_DIRECTORY)
            log_test(f"✅ Navigation vers {FTP_DIRECTORY}", "SUCCESS")
        except Exception as nav_error:
            log_test(f"❌ Navigation échouée: {nav_error}", "ERROR")
            ftp.quit()
            return False
        
        # Test d'upload rapide
        test_filename = f"test_patch29_{mode_name.lower()}_{int(time.time())}.txt"
        test_content = f"Test mode {mode_name} - {datetime.now()}"
        test_file = BytesIO(test_content.encode('utf-8'))
        
        log_test(f"Test upload {mode_name}...", "INFO")
        start_time = time.time()
        
        try:
            ftp.storbinary(f'STOR {test_filename}', test_file, blocksize=1024)
            upload_time = time.time() - start_time
            log_test(f"✅ Upload {mode_name} réussi en {upload_time:.2f}s", "SUCCESS")
            
            # Vérification rapide
            try:
                file_size = ftp.size(test_filename)
                log_test(f"✅ Fichier confirmé ({file_size} bytes)", "SUCCESS")
                
                # URL publique générée
                public_url = f"https://{FTP_HOST}/wordpress/uploads/{test_filename}"
                log_test(f"🌐 URL publique: {public_url}", "INFO")
                
                # Nettoyage
                try:
                    ftp.delete(test_filename)
                    log_test("✅ Fichier test supprimé", "SUCCESS")
                except:
                    log_test("⚠️ Suppression impossible (normal)", "WARNING")
                    
            except Exception as size_error:
                log_test(f"⚠️ Vérification impossible: {size_error}", "WARNING")
            
            ftp.quit()
            log_test(f"✅ MODE {mode_name} - SUCCÈS COMPLET", "SUCCESS")
            return True
            
        except Exception as upload_error:
            upload_time = time.time() - start_time
            log_test(f"❌ Upload {mode_name} échoué en {upload_time:.2f}s: {upload_error}", "ERROR")
            ftp.quit()
            return False
        
    except Exception as e:
        log_test(f"❌ Mode {mode_name} échoué: {e}", "ERROR")
        return False

def test_all_ftp_modes():
    """Test tous les modes FTP"""
    log_test("=== PATCH 29: TEST COMPLET DES MODES FTP ===", "INFO")
    
    modes = [
        {"passive": True, "timeout": 10, "name": "PASSIF RAPIDE"},
        {"passive": False, "timeout": 10, "name": "ACTIF RAPIDE"},
        {"passive": True, "timeout": 20, "name": "PASSIF STANDARD"},
        {"passive": False, "timeout": 20, "name": "ACTIF STANDARD"}
    ]
    
    results = []
    
    for mode in modes:
        log_test(f"\n--- Test {mode['name']} ---", "INFO")
        success = test_ftp_mode(mode["passive"], mode["timeout"])
        results.append({"mode": mode["name"], "success": success})
        
        if success:
            log_test(f"✅ {mode['name']} - RECOMMANDÉ POUR PRODUCTION", "SUCCESS")
            break  # Arrêter au premier mode qui fonctionne
        else:
            log_test(f"❌ {mode['name']} - NON VIABLE", "ERROR")
            time.sleep(2)  # Attendre avant le test suivant
    
    # Résumé
    log_test("\n=== RÉSUMÉ DES TESTS ===", "INFO")
    working_modes = [r for r in results if r["success"]]
    
    if working_modes:
        log_test(f"✅ Modes FTP fonctionnels: {len(working_modes)}", "SUCCESS")
        for result in results:
            status = "✅ FONCTIONNEL" if result["success"] else "❌ DÉFAILLANT"
            log_test(f"  • {result['mode']}: {status}", "SUCCESS" if result["success"] else "ERROR")
        
        log_test("\n🎯 CONFIGURATION RECOMMANDÉE:", "SUCCESS")
        best_mode = working_modes[0]
        log_test(f"Mode: {best_mode['mode']}", "SUCCESS")
        log_test(f"Host: {FTP_HOST}", "SUCCESS")
        log_test(f"User: {FTP_USER}", "SUCCESS") 
        log_test(f"Password: {FTP_PASSWORD}", "SUCCESS")
        log_test(f"Directory: {FTP_DIRECTORY}", "SUCCESS")
        log_test(f"URL Base: https://{FTP_HOST}/wordpress/uploads/", "SUCCESS")
        
        return True
    else:
        log_test("❌ AUCUN MODE FTP FONCTIONNEL", "ERROR")
        log_test("💡 Actions recommandées:", "INFO")
        log_test("  1. Vérifier les credentials FTP", "INFO")
        log_test("  2. Vérifier la connectivité réseau", "INFO")
        log_test("  3. Contacter l'hébergeur", "INFO")
        return False

if __name__ == "__main__":
    success = test_all_ftp_modes()
    if success:
        print("\n🎉 PATCH 29 - FTP OPÉRATIONNEL!")
        print("Les publications Facebook/Instagram peuvent maintenant utiliser FTP.")
    else:
        print("\n❌ PATCH 29 - PROBLÈME FTP PERSISTANT")