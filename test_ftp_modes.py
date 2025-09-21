#!/usr/bin/env python3
"""
Test FTP avec modes passif/actif pour résoudre les timeouts
"""

import ftplib
import os
import tempfile
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

FTP_HOST = os.getenv("FTP_HOST", "logicamp.org")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER", "logi")
FTP_PASSWORD = os.getenv("FTP_PASSWORD", "logi")
FTP_DIRECTORY = os.getenv("FTP_DIRECTORY", "/wordpress/uploads/")

def log_test(message: str, level: str = "INFO"):
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
    icon = icons.get(level.upper(), "📋")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{icon} [{timestamp}] [FTP] {message}")

def test_ftp_mode(passive_mode=True, timeout=10):
    """Test FTP avec mode spécifique"""
    mode_name = "PASSIF" if passive_mode else "ACTIF"
    log_test(f"=== TEST MODE {mode_name} (timeout: {timeout}s) ===", "TEST")
    
    try:
        ftp = ftplib.FTP()
        ftp.set_pasv(passive_mode)
        ftp.connect(FTP_HOST, FTP_PORT, timeout=timeout)
        ftp.login(FTP_USER, FTP_PASSWORD)
        
        log_test(f"✅ Connexion et authentification OK (mode {mode_name})", "SUCCESS")
        
        # Test navigation
        try:
            ftp.cwd(FTP_DIRECTORY)
            log_test(f"✅ Navigation réussie vers {FTP_DIRECTORY}", "SUCCESS")
        except:
            log_test(f"⚠️ Navigation échouée vers {FTP_DIRECTORY}", "WARNING")
        
        # Test listing avec timeout court
        try:
            log_test("Test listing...", "INFO")
            file_list = []
            ftp.retrlines('LIST', file_list.append)
            log_test(f"✅ Listing réussi - {len(file_list)} éléments", "SUCCESS")
        except Exception as e:
            log_test(f"❌ Listing échoué: {str(e)}", "ERROR")
            raise e
        
        # Test upload simple
        try:
            log_test("Test upload simple...", "INFO")
            test_content = f"Test FTP {mode_name} - {datetime.now()}"
            test_filename = f"test_{mode_name.lower()}_{int(time.time())}.txt"
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
                temp_file.write(test_content)
                temp_file_path = temp_file.name
            
            with open(temp_file_path, 'rb') as test_file:
                ftp.storbinary(f'STOR {test_filename}', test_file, blocksize=1024)
            
            log_test(f"✅ Upload réussi: {test_filename}", "SUCCESS")
            
            # Nettoyage
            try:
                ftp.delete(test_filename)
                log_test("🧹 Fichier de test supprimé", "INFO")
            except:
                pass
            
            os.unlink(temp_file_path)
            
        except Exception as e:
            log_test(f"❌ Upload échoué: {str(e)}", "ERROR")
            raise e
        
        ftp.quit()
        log_test(f"✅ Mode {mode_name} FONCTIONNE !", "SUCCESS")
        return True
        
    except Exception as e:
        log_test(f"❌ Mode {mode_name} échoué: {str(e)}", "ERROR")
        return False

def test_all_configurations():
    """Test toutes les configurations possibles"""
    log_test("🚀 TEST DE TOUTES LES CONFIGURATIONS FTP", "TEST")
    
    configurations = [
        {"passive": True, "timeout": 10, "name": "Passif rapide"},
        {"passive": False, "timeout": 10, "name": "Actif rapide"},
        {"passive": True, "timeout": 30, "name": "Passif standard"},
        {"passive": False, "timeout": 30, "name": "Actif standard"},
    ]
    
    working_configs = []
    
    for config in configurations:
        print()
        try:
            if test_ftp_mode(config["passive"], config["timeout"]):
                working_configs.append(config)
                log_test(f"🎉 Configuration recommandée trouvée: {config['name']}", "SUCCESS")
        except:
            continue
    
    print()
    log_test("=== RÉSUMÉ ===", "SUCCESS")
    if working_configs:
        log_test(f"✅ {len(working_configs)} configuration(s) fonctionnelle(s) trouvée(s)", "SUCCESS")
        for config in working_configs:
            passive_str = "True" if config["passive"] else "False"
            log_test(f"  • {config['name']}: set_pasv({passive_str}), timeout={config['timeout']}", "SUCCESS")
        
        # Recommandation
        best_config = working_configs[0]
        log_test("💡 RECOMMANDATION:", "SUCCESS")
        log_test(f"Utiliser mode {'PASSIF' if best_config['passive'] else 'ACTIF'} avec timeout {best_config['timeout']}s", "SUCCESS")
        
        return best_config
    else:
        log_test("❌ Aucune configuration fonctionnelle trouvée", "ERROR")
        return None

if __name__ == "__main__":
    print()
    print("🔧 DIAGNOSTIC FTP - Modes de Connexion")
    print("=" * 50)
    
    best_config = test_all_configurations()
    
    if best_config:
        print()
        log_test("🎯 SOLUTION POUR LE CODE:", "SUCCESS")
        log_test("Modifier la fonction upload_video_to_ftp() :", "INFO")
        log_test(f"ftp.set_pasv({best_config['passive']})", "INFO")
        log_test(f"ftp.connect(FTP_HOST, FTP_PORT, timeout={best_config['timeout']})", "INFO")
    
    print()
    print("=" * 50)