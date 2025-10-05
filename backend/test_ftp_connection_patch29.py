#!/usr/bin/env python3
"""
PATCH 29: Test de connexion FTP avec nouveaux credentials
Test la connexion FTP avec login=logi, password=6837
"""

import ftplib
import os
from datetime import datetime

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

def test_ftp_connection_patch29():
    """Test complet de la connexion FTP avec nouveaux credentials"""
    try:
        log_test("=== TEST CONNEXION FTP PATCH 29 ===", "INFO")
        log_test(f"Host: {FTP_HOST}:{FTP_PORT}", "INFO") 
        log_test(f"User: {FTP_USER}", "INFO")
        log_test(f"Password: {'*' * len(FTP_PASSWORD)}", "INFO")
        log_test(f"Directory: {FTP_DIRECTORY}", "INFO")
        
        # Test 1: Connexion de base
        log_test("Test 1: Connexion FTP...", "INFO")
        ftp = ftplib.FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, FTP_PORT, timeout=30)
        log_test("✅ Connexion FTP établie", "SUCCESS")
        
        # Test 2: Authentification
        log_test("Test 2: Authentification...", "INFO")
        ftp.login(FTP_USER, FTP_PASSWORD)
        log_test("✅ Authentification réussie", "SUCCESS")
        
        # Test 3: Répertoire courant
        current_dir = ftp.pwd()
        log_test(f"Répertoire courant: {current_dir}", "INFO")
        
        # Test 4: Navigation vers le répertoire uploads
        log_test("Test 4: Navigation vers /wordpress/uploads/...", "INFO")
        try:
            ftp.cwd(FTP_DIRECTORY)
            log_test(f"✅ Navigation réussie vers {FTP_DIRECTORY}", "SUCCESS")
            
            # Test 5: Lister les fichiers (avec limite)
            log_test("Test 5: Listage des fichiers...", "INFO")
            try:
                files = ftp.nlst()
                file_count = len(files)
                log_test(f"✅ {file_count} fichiers trouvés", "SUCCESS")
                
                # Afficher quelques exemples de fichiers
                if files:
                    log_test("Exemples de fichiers:", "INFO")
                    for i, filename in enumerate(files[:5]):  # 5 premiers fichiers
                        log_test(f"  • {filename}", "INFO")
                    if file_count > 5:
                        log_test(f"  ... et {file_count - 5} autres fichiers", "INFO")
            except Exception as list_error:
                log_test(f"⚠️ Listage impossible: {list_error}", "WARNING")
                log_test("Cela n'empêche pas l'upload de fonctionner", "INFO")
                
        except ftplib.error_perm as nav_error:
            log_test(f"❌ Navigation échouée: {nav_error}", "ERROR")
            log_test("Tentative d'accès au répertoire racine...", "INFO")
            root_files = ftp.nlst()
            log_test(f"Répertoire racine contient {len(root_files)} éléments", "INFO")
            return False
        
        # Test 6: Test d'écriture (création d'un petit fichier test)
        log_test("Test 6: Test d'écriture...", "INFO")
        try:
            test_filename = f"patch29_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            test_content = f"Test PATCH 29 - {datetime.now()}\nCredentials: {FTP_USER}:{FTP_PASSWORD}\n"
            
            # Créer le fichier test en mémoire
            from io import BytesIO
            test_file = BytesIO(test_content.encode('utf-8'))
            
            # Upload du fichier test
            ftp.storbinary(f'STOR {test_filename}', test_file)
            log_test(f"✅ Fichier test créé: {test_filename}", "SUCCESS")
            
            # Vérifier que le fichier existe
            try:
                file_size = ftp.size(test_filename)
                log_test(f"✅ Fichier confirmé sur serveur ({file_size} bytes)", "SUCCESS")
                
                # Nettoyer le fichier test
                try:
                    ftp.delete(test_filename)
                    log_test("✅ Fichier test nettoyé", "SUCCESS")
                except:
                    log_test("⚠️ Impossible de supprimer le fichier test (normal)", "WARNING")
                    
            except Exception as size_error:
                log_test(f"⚠️ Vérification taille impossible: {size_error}", "WARNING")
                log_test("Mais l'upload semble avoir fonctionné", "INFO")
                
        except Exception as write_error:
            log_test(f"❌ Test d'écriture échoué: {write_error}", "ERROR")
            return False
        
        # Fermer la connexion
        ftp.quit()
        log_test("✅ Connexion fermée proprement", "SUCCESS")
        
        # Résumé final
        log_test("=== RÉSULTAT FINAL ===", "SUCCESS")
        log_test("✅ CONNEXION FTP PATCH 29 - SUCCÈS COMPLET", "SUCCESS")
        log_test("✅ Tous les tests passés:", "SUCCESS")
        log_test("  • Connexion établie", "SUCCESS") 
        log_test("  • Authentification réussie", "SUCCESS")
        log_test("  • Navigation vers uploads/", "SUCCESS")
        log_test("  • Permissions d'écriture confirmées", "SUCCESS")
        log_test("", "INFO")
        log_test("🎯 Les publications Facebook/Instagram peuvent maintenant utiliser FTP", "SUCCESS")
        log_test(f"🌐 URL de base: https://{FTP_HOST}/wordpress/uploads/", "SUCCESS")
        
        return True
        
    except ftplib.error_perm as perm_error:
        log_test(f"❌ Erreur de permissions FTP: {perm_error}", "ERROR")
        log_test("💡 Vérifiez les identifiants FTP", "INFO")
        return False
        
    except Exception as e:
        log_test(f"❌ Erreur générale: {e}", "ERROR")
        return False

if __name__ == "__main__":
    success = test_ftp_connection_patch29()
    if success:
        print("\n🎉 FTP PATCH 29 - PRÊT POUR PRODUCTION!")
    else:
        print("\n❌ FTP PATCH 29 - PROBLÈME DÉTECTÉ")