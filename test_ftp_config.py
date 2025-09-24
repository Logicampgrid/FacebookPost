#!/usr/bin/env python3
"""
Test de la configuration FTP avec le mot de passe "logi"
"""

import sys
sys.path.insert(0, '/app/backend')

from server import FTP_HOST, FTP_PORT, FTP_USER, FTP_PASSWORD, FTP_DIRECTORY

def test_ftp_config():
    """Test la configuration FTP"""
    print("=== CONFIGURATION FTP ===")
    print(f"🌐 Host: {FTP_HOST}")
    print(f"🚪 Port: {FTP_PORT}")
    print(f"👤 User: {FTP_USER}")
    print(f"🔐 Password: {FTP_PASSWORD}")
    print(f"📂 Directory: {FTP_DIRECTORY}")
    
    # Vérifier que le mot de passe est bien "logi"
    if FTP_PASSWORD == "logi":
        print("✅ Mot de passe FTP configuré correctement: 'logi'")
        return True
    else:
        print(f"❌ Mot de passe FTP incorrect: '{FTP_PASSWORD}' (attendu: 'logi')")
        return False

if __name__ == "__main__":
    success = test_ftp_config()
    sys.exit(0 if success else 1)