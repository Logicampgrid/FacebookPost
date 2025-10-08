#!/usr/bin/env python3
"""
Test de la structure de répertoires FTP
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

def test_ftp_directory_structure():
    """Explore la structure de répertoires FTP"""
    
    FTP_HOST = "logicamp.org"
    FTP_PORT = 21
    FTP_USER = "logi"
    FTP_PASSWORD = "logi"
    
    log_test("🧪 Exploration de la structure FTP", "INFO")
    
    try:
        ftp = ftplib.FTP()
        ftp.set_pasv(True)
        ftp.connect(FTP_HOST, FTP_PORT, timeout=15)
        ftp.login(FTP_USER, FTP_PASSWORD)
        
        # Explorer le répertoire racine
        log_test("📁 Répertoire racine:", "INFO")
        try:
            current_dir = ftp.pwd()
            log_test(f"   PWD: {current_dir}", "INFO")
            
            files = ftp.nlst()
            for f in files[:10]:  # Limite à 10 pour éviter trop de sortie
                log_test(f"   - {f}", "INFO")
            
            if len(files) > 10:
                log_test(f"   ... et {len(files) - 10} autres fichiers/dossiers", "INFO")
                
        except Exception as e:
            log_test(f"❌ Erreur listage racine: {e}", "ERROR")
        
        # Tester différents chemins possibles
        possible_paths = [
            "/www/wordpress/uploads/",
            "/wordpress/uploads/", 
            "/public_html/wordpress/uploads/",
            "/httpdocs/wordpress/uploads/",
            "/uploads/",
            "/www/uploads/",
            "/public_html/uploads/",
            "/httpdocs/uploads/",
            "www/wordpress/uploads/",
            "wordpress/uploads/",
        ]
        
        log_test("\n🔍 Test des chemins possibles:", "INFO")
        
        for path in possible_paths:
            try:
                log_test(f"Test: {path}", "INFO")
                ftp.cwd(path)
                
                # Si on arrive ici, le chemin existe
                files = ftp.nlst()
                log_test(f"✅ SUCCÈS: {path} - {len(files)} fichiers", "SUCCESS")
                
                # Afficher quelques fichiers
                for f in files[:3]:
                    log_test(f"   - {f}", "INFO")
                
                # Retourner à la racine pour le prochain test
                ftp.cwd("/")
                
                return path
                
            except Exception as e:
                log_test(f"❌ Échec: {e}", "WARNING")
                try:
                    ftp.cwd("/")  # Retour racine en cas d'erreur
                except:
                    pass
        
        ftp.quit()
        return None
        
    except Exception as e:
        log_test(f"❌ Erreur connexion: {e}", "ERROR")
        return None

if __name__ == "__main__":
    working_path = test_ftp_directory_structure()
    
    if working_path:
        print(f"\n✅ CHEMIN FONCTIONNEL TROUVÉ: {working_path}")
        print("🔧 Mettre à jour FTP_DIRECTORY dans le .env !")
    else:
        print("\n❌ AUCUN CHEMIN FONCTIONNEL TROUVÉ")
        print("🔍 Vérifier les permissions ou la configuration du serveur FTP")