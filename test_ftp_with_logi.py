#!/usr/bin/env python3
"""
Test FTP avec différents mots de passe
"""

import os
import ftplib
from datetime import datetime

def log_test(message: str, level: str = "INFO"):
    """Logging pour les tests"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [FTP TEST] {message}")

def test_ftp_credentials():
    """Test FTP avec différentes combinaisons de credentials"""
    
    FTP_HOST = "logicamp.org"
    FTP_PORT = 21
    FTP_DIRECTORY = "/www/wordpress/uploads/"
    
    # Différentes combinaisons à tester
    credentials = [
        ("logi", "logi"),
        ("logi", "6837"),
        ("logicamp", "logi"),
        ("logicamp", "6837"),
        ("wordpress", "logi"),
        ("wordpress", "6837"),
    ]
    
    log_test("🧪 Test de différents credentials FTP", "INFO")
    
    for user, password in credentials:
        log_test(f"Test: {user} / {'*' * len(password)}", "INFO")
        
        try:
            ftp = ftplib.FTP()
            ftp.set_pasv(True)
            ftp.connect(FTP_HOST, FTP_PORT, timeout=15)
            ftp.login(user, password)
            
            # Test navigation
            try:
                ftp.cwd(FTP_DIRECTORY)
                log_test(f"✅ SUCCÈS: {user}:{password} - Navigation OK", "SUCCESS")
                
                # Test liste
                files = ftp.nlst()
                log_test(f"📁 {len(files)} fichiers dans le répertoire", "SUCCESS")
                
                ftp.quit()
                return user, password
                
            except Exception as nav_error:
                log_test(f"❌ Navigation échouée: {nav_error}", "WARNING")
                ftp.quit()
            
        except Exception as e:
            log_test(f"❌ Échec: {e}", "WARNING")
            try:
                ftp.quit()
            except:
                pass
        
        print()  # Ligne vide pour clarté
    
    return None, None

if __name__ == "__main__":
    success_user, success_pass = test_ftp_credentials()
    
    if success_user:
        print(f"\n✅ CREDENTIALS FONCTIONNELS TROUVÉS:")
        print(f"   User: {success_user}")
        print(f"   Password: {success_pass}")
        print("\n🔧 Mettre à jour le .env avec ces credentials !")
    else:
        print("\n❌ AUCUN CREDENTIAL FONCTIONNEL TROUVÉ")
        print("🔍 Il peut y avoir un problème de serveur FTP ou de firewall")