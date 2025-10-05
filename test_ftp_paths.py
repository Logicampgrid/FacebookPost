#!/usr/bin/env python3
"""
PATCH 32 - Diagnostic des chemins FTP pour trouver le bon répertoire
"""

import ftplib
import os

def test_ftp_paths():
    """Test différents chemins FTP pour trouver le bon répertoire"""
    
    # Configuration FTP actuelle
    FTP_HOST = "logicamp.org"
    FTP_USER = "logi"  
    FTP_PASSWORD = "6837"
    
    # Chemins à tester
    paths_to_test = [
        "/wordpress/uploads/",     # Chemin actuel
        "/www/wordpress/uploads/", # Chemin suggéré par l'utilisateur
        "/public_html/wordpress/uploads/",
        "/htdocs/wordpress/uploads/",
        "/wordpress/wp-content/uploads/",
        "/www/wordpress/wp-content/uploads/",
        "/",  # Racine pour explorer
    ]
    
    print("🔧 DIAGNOSTIC FTP PATHS - PATCH 32")
    print("=" * 50)
    
    try:
        # Connexion FTP
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, 21)
        ftp.login(FTP_USER, FTP_PASSWORD)
        
        print(f"✅ Connexion FTP réussie à {FTP_HOST}")
        print(f"📁 Répertoire racine: {ftp.pwd()}")
        
        # Test 1: Explorer la racine
        print(f"\n📋 Contenu de la racine ({ftp.pwd()}):")
        try:
            items = ftp.nlst()
            for item in items[:10]:  # Limite à 10 éléments
                print(f"  • {item}")
            if len(items) > 10:
                print(f"  ... et {len(items)-10} autres éléments")
        except Exception as e:
            print(f"❌ Erreur listage racine: {e}")
        
        # Test 2: Tester chaque chemin
        print(f"\n🧪 Test des chemins possibles:")
        
        for path in paths_to_test:
            print(f"\n🔍 Test: {path}")
            try:
                # Revenir à la racine
                ftp.cwd("/")
                
                if path == "/":
                    print(f"  ✅ Racine accessible")
                    continue
                    
                # Tenter de naviguer vers le chemin
                ftp.cwd(path)
                print(f"  ✅ Chemin accessible!")
                
                # Tester écriture
                test_filename = "test_patch32_access.txt"
                try:
                    ftp.storbinary(f'STOR {test_filename}', 
                                 io.BytesIO(b"Test PATCH 32"))
                    print(f"  ✅ Écriture possible")
                    
                    # Vérifier URL correspondante
                    test_url = f"https://logicamp.org{path}{test_filename}"
                    print(f"  🌐 URL de test: {test_url}")
                    
                    # Supprimer le fichier de test
                    try:
                        ftp.delete(test_filename)
                        print(f"  ✅ Suppression test réussie")
                    except:
                        print(f"  ⚠️ Impossible de supprimer le fichier test")
                        
                except Exception as e:
                    print(f"  ❌ Écriture impossible: {e}")
                    
            except Exception as e:
                print(f"  ❌ Chemin inaccessible: {e}")
        
        # Test 3: Chercher des indices WordPress
        print(f"\n🔍 Recherche d'indices WordPress:")
        try:
            ftp.cwd("/")
            items = ftp.nlst()
            
            wp_indicators = []
            for item in items:
                if "www" in item.lower() or "public" in item.lower() or "html" in item.lower():
                    wp_indicators.append(item)
            
            if wp_indicators:
                print(f"📁 Répertoires suspects trouvés:")
                for item in wp_indicators:
                    print(f"  • {item}")
                    
                    # Explorer le premier répertoire suspect
                    if item == wp_indicators[0]:
                        try:
                            ftp.cwd(f"/{item}")
                            sub_items = ftp.nlst()
                            print(f"  📋 Contenu de {item}:")
                            for sub_item in sub_items[:5]:
                                print(f"    - {sub_item}")
                        except Exception as e:
                            print(f"  ❌ Impossible d'explorer {item}: {e}")
            else:
                print("❌ Aucun répertoire web évident trouvé")
                        
        except Exception as e:
            print(f"❌ Erreur exploration: {e}")
            
        ftp.quit()
        
    except Exception as e:
        print(f"❌ Erreur connexion FTP: {e}")

if __name__ == "__main__":
    import io
    test_ftp_paths()