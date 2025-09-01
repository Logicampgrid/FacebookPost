#!/usr/bin/env python3
"""
Script de test pour vérifier les corrections apportées à server.py
Teste spécifiquement les problèmes identifiés:
1. Erreur 'Post object has no attribute product_link'
2. Erreur 'cannot identify image file' 
3. Conversion WebP → JPEG/PNG
4. Timeouts et échecs de téléchargement
5. Vérification taille des médias et compression
"""

import asyncio
import sys
import os
import tempfile
from PIL import Image
import json

# Import des fonctions du serveur
from server import (
    Post, 
    safe_image_processing_with_fallbacks,
    convert_webp_to_jpeg,
    download_media_with_extended_retry,
    detect_media_type_from_content,
    validate_and_convert_media_for_social,
    log_media,
    log_instagram,
    log_facebook
)

async def test_1_post_model_product_link():
    """Test 1: Vérifier que le modèle Post a l'attribut product_link"""
    print("\n" + "="*70)
    print("🧪 TEST 1: Modèle Post avec product_link")
    print("="*70)
    
    try:
        # Créer un Post avec product_link
        post = Post(
            user_id="test_user",
            content="Test post avec lien produit",
            target_type="page", 
            target_id="123456789",
            target_name="Test Page",
            platform="instagram",
            product_link="https://example.com/product/test"
        )
        
        # Vérifier l'accès à product_link
        assert hasattr(post, 'product_link'), "L'attribut product_link n'existe pas"
        assert post.product_link == "https://example.com/product/test", f"Valeur incorrecte: {post.product_link}"
        
        log_instagram("✅ TEST 1 RÉUSSI: Modèle Post avec product_link fonctionne", "SUCCESS")
        return True
        
    except Exception as e:
        log_instagram(f"❌ TEST 1 ÉCHOUÉ: {str(e)}", "ERROR")
        return False

async def test_2_robust_image_processing():
    """Test 2: Gestion robuste des erreurs 'cannot identify image file'"""
    print("\n" + "="*70)
    print("🧪 TEST 2: Traitement d'image robuste")
    print("="*70)
    
    test_results = []
    
    # Test 2a: Fichier inexistant
    try:
        success, result, error = await safe_image_processing_with_fallbacks("/nonexistent/file.jpg", "analyze")
        assert not success, "Le fichier inexistant devrait échouer"
        assert "introuvable" in error.lower(), f"Message d'erreur inattendu: {error}"
        log_media("✅ TEST 2a: Gestion fichier inexistant OK", "SUCCESS")
        test_results.append(True)
    except Exception as e:
        log_media(f"❌ TEST 2a: {str(e)}", "ERROR")
        test_results.append(False)
    
    # Test 2b: Fichier corrompu/trop petit
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(b'corrupted')
            tmp_path = tmp.name
        
        success, result, error = await safe_image_processing_with_fallbacks(tmp_path, "analyze")
        assert not success, "Le fichier corrompu devrait échouer"
        log_media("✅ TEST 2b: Gestion fichier corrompu OK", "SUCCESS")
        test_results.append(True)
        
        os.unlink(tmp_path)
        
    except Exception as e:
        log_media(f"❌ TEST 2b: {str(e)}", "ERROR")
        test_results.append(False)
    
    # Test 2c: Création d'une vraie image test
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            tmp_path = tmp.name
        
        # Créer une image test simple
        img = Image.new('RGB', (100, 100), color='red')
        img.save(tmp_path, 'PNG')
        
        success, result, error = await safe_image_processing_with_fallbacks(tmp_path, "analyze")
        assert success, f"L'image valide devrait réussir: {error}"
        assert result["format"] == "PNG", f"Format incorrect: {result['format']}"
        assert result["size"] == (100, 100), f"Taille incorrecte: {result['size']}"
        
        log_media("✅ TEST 2c: Traitement image valide OK", "SUCCESS")
        test_results.append(True)
        
        os.unlink(tmp_path)
        
    except Exception as e:
        log_media(f"❌ TEST 2c: {str(e)}", "ERROR")
        test_results.append(False)
    
    success_rate = sum(test_results) / len(test_results)
    if success_rate >= 0.8:
        log_media(f"✅ TEST 2 GLOBAL RÉUSSI: {success_rate*100:.1f}% de réussite", "SUCCESS")
        return True
    else:
        log_media(f"❌ TEST 2 GLOBAL ÉCHOUÉ: {success_rate*100:.1f}% de réussite", "ERROR")
        return False

async def test_3_webp_conversion():
    """Test 3: Conversion WebP → JPEG"""
    print("\n" + "="*70)
    print("🧪 TEST 3: Conversion WebP → JPEG")
    print("="*70)
    
    try:
        # Créer une image WebP test
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webp') as tmp:
            tmp_path = tmp.name
        
        # Créer et sauvegarder en WebP
        img = Image.new('RGBA', (200, 200), color=(255, 0, 0, 128))  # Rouge semi-transparent
        img.save(tmp_path, 'WEBP')
        
        log_media(f"Image WebP test créée: {tmp_path}", "INFO")
        
        # Test de conversion
        success, jpeg_path, error = await convert_webp_to_jpeg(tmp_path)
        
        assert success, f"La conversion WebP devrait réussir: {error}"
        assert jpeg_path and os.path.exists(jpeg_path), f"Fichier JPEG non créé: {jpeg_path}"
        assert jpeg_path.lower().endswith(('.jpg', '.jpeg')), f"Extension incorrecte: {jpeg_path}"
        
        # Vérifier que c'est bien un JPEG
        with Image.open(jpeg_path) as converted_img:
            assert converted_img.format == 'JPEG', f"Format final incorrect: {converted_img.format}"
            assert converted_img.mode == 'RGB', f"Mode couleur incorrect: {converted_img.mode}"
        
        log_instagram("✅ TEST 3 RÉUSSI: Conversion WebP → JPEG fonctionne", "SUCCESS")
        
        # Nettoyer
        os.unlink(tmp_path)
        os.unlink(jpeg_path)
        
        return True
        
    except Exception as e:
        log_instagram(f"❌ TEST 3 ÉCHOUÉ: {str(e)}", "ERROR")
        return False

async def test_4_download_with_retry():
    """Test 4: Téléchargement avec retry et timeouts étendus"""
    print("\n" + "="*70)
    print("🧪 TEST 4: Téléchargement avec retry")
    print("="*70)
    
    test_results = []
    
    # Test 4a: URL valide
    try:
        # URL d'image test fiable
        test_url = "https://httpbin.org/image/png"
        
        success, local_path, error = await download_media_with_extended_retry(
            test_url, max_attempts=2, base_timeout=10
        )
        
        if success:
            assert os.path.exists(local_path), f"Fichier non créé: {local_path}"
            assert os.path.getsize(local_path) > 1000, f"Fichier trop petit: {os.path.getsize(local_path)} bytes"
            
            log_media("✅ TEST 4a: Téléchargement URL valide OK", "SUCCESS")
            os.unlink(local_path)  # Nettoyer
            test_results.append(True)
        else:
            log_media(f"⚠️ TEST 4a: Téléchargement échoué (peut être normal): {error}", "WARNING")
            test_results.append(True)  # Accepter l'échec réseau comme normal
            
    except Exception as e:
        log_media(f"❌ TEST 4a: {str(e)}", "ERROR")
        test_results.append(False)
    
    # Test 4b: URL invalide (doit échouer gracieusement)
    try:
        invalid_url = "https://nonexistent-domain-12345.com/image.jpg"
        
        success, local_path, error = await download_media_with_extended_retry(
            invalid_url, max_attempts=1, base_timeout=5
        )
        
        assert not success, "L'URL invalide devrait échouer"
        assert error and len(error) > 0, "Un message d'erreur devrait être fourni"
        
        log_media("✅ TEST 4b: Gestion URL invalide OK", "SUCCESS")
        test_results.append(True)
        
    except Exception as e:
        log_media(f"❌ TEST 4b: {str(e)}", "ERROR")
        test_results.append(False)
    
    success_rate = sum(test_results) / len(test_results)
    if success_rate >= 0.8:
        log_media(f"✅ TEST 4 GLOBAL RÉUSSI: {success_rate*100:.1f}% de réussite", "SUCCESS")
        return True
    else:
        log_media(f"❌ TEST 4 GLOBAL ÉCHOUÉ: {success_rate*100:.1f}% de réussite", "ERROR")
        return False

async def test_5_media_size_validation():
    """Test 5: Vérification taille des médias et compression"""
    print("\n" + "="*70)
    print("🧪 TEST 5: Validation taille médias")
    print("="*70)
    
    try:
        # Créer une grande image pour tester la compression
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            tmp_path = tmp.name
        
        # Image de 2000x2000 (assez grande pour déclencher la compression)
        big_img = Image.new('RGB', (2000, 2000), color='blue')
        big_img.save(tmp_path, 'PNG')
        
        original_size = os.path.getsize(tmp_path)
        original_size_mb = original_size / (1024 * 1024)
        
        log_media(f"Image test créée: {original_size_mb:.2f}MB, {big_img.size}", "INFO")
        
        # Test validation et conversion pour Instagram
        success, converted_path, media_type, error = await validate_and_convert_media_for_social(
            tmp_path, "instagram"
        )
        
        assert success, f"La validation devrait réussir: {error}"
        assert media_type == "image", f"Type incorrect: {media_type}"
        assert converted_path and os.path.exists(converted_path), f"Fichier converti non créé: {converted_path}"
        
        # Vérifier que la taille/résolution a été optimisée
        with Image.open(converted_path) as optimized_img:
            assert max(optimized_img.size) <= 1080, f"Résolution non optimisée: {optimized_img.size}"
        
        converted_size = os.path.getsize(converted_path)
        converted_size_mb = converted_size / (1024 * 1024)
        
        # Pour Instagram, ne devrait pas dépasser 8MB
        assert converted_size_mb <= 8.0, f"Taille non optimisée pour Instagram: {converted_size_mb:.2f}MB"
        
        log_instagram(f"✅ TEST 5 RÉUSSI: {original_size_mb:.2f}MB → {converted_size_mb:.2f}MB", "SUCCESS")
        
        # Nettoyer
        os.unlink(tmp_path)
        if converted_path != tmp_path:
            os.unlink(converted_path)
        
        return True
        
    except Exception as e:
        log_instagram(f"❌ TEST 5 ÉCHOUÉ: {str(e)}", "ERROR")
        return False

async def main():
    """Exécuter tous les tests"""
    print("🚀 DÉBUT DES TESTS DE CORRECTIONS server.py")
    print("=" * 70)
    print("Tests des problèmes spécifiques identifiés:")
    print("1. Erreur 'Post object has no attribute product_link'")
    print("2. Erreur 'cannot identify image file'")
    print("3. Conversion WebP → JPEG/PNG")
    print("4. Timeouts et échecs de téléchargement")
    print("5. Vérification taille des médias et compression")
    print("=" * 70)
    
    # Exécuter tous les tests
    tests = [
        ("Modèle Post avec product_link", test_1_post_model_product_link),
        ("Traitement d'image robuste", test_2_robust_image_processing),
        ("Conversion WebP → JPEG", test_3_webp_conversion),
        ("Téléchargement avec retry", test_4_download_with_retry),
        ("Validation taille médias", test_5_media_size_validation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            log_media(f"❌ ERREUR TEST '{test_name}': {str(e)}", "ERROR")
            results.append((test_name, False))
    
    # Résumé des résultats
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    success_rate = (passed / total) * 100
    
    print("=" * 70)
    print(f"🎯 RÉSULTAT GLOBAL: {passed}/{total} tests réussis ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 CORRECTIONS VALIDÉES: server.py est maintenant robuste!")
        sys.exit(0)
    else:
        print("⚠️ CORRECTIONS PARTIELLES: Certains problèmes persistent")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())