async def detect_media_type_from_content(content: bytes, filename: str = None) -> str:
    """
    Détection automatique ULTRA-ROBUSTE du type de média (image ou vidéo)
    Version renforcée pour résoudre les problèmes de détection MP4 et améliorer la fiabilité
    
    Args:
        content: Contenu binaire du fichier
        filename: Nom de fichier optionnel pour hint d'extension
    
    Returns:
        str: 'image' ou 'video'
    """
    try:
        print(f"🔍 DÉTECTION MÉDIA ULTRA-ROBUSTE: Analyse de {len(content)} bytes, filename: {filename}")
        
        detected_type = None
        detection_method = ""
        confidence_score = 0
        
        # Étape 1: Détection par extension de fichier (priorité haute)
        if filename:
            # Nettoyer filename des paramètres URL et caractères indésirables
            clean_filename = filename.split('?')[0].split('#')[0].strip()
            ext = clean_filename.lower().split('.')[-1] if '.' in clean_filename else ''
            print(f"🔍 Extension détectée: '{ext}' depuis filename: {clean_filename}")
            
            # Extensions vidéo avec priorité spéciale pour MP4 (Instagram)
            video_extensions = {
                'mp4': 95,   # Priorité maximale pour Instagram
                'mov': 90,   # QuickTime, bien supporté
                'm4v': 85,   # Variant MP4
                'avi': 70,   # Plus ancien mais supporté
                'webm': 75,  # Web moderne
                'mkv': 60,   # Container flexible
                'flv': 50,   # Flash legacy
                '3gp': 40,   # Mobile legacy
                'wmv': 45    # Windows Media
            }
            
            # Extensions image avec optimisation Facebook/Instagram
            image_extensions = {
                'jpg': 95,   # Format prioritaire Facebook/Instagram
                'jpeg': 95,  # Idem
                'png': 90,   # Très bien supporté
                'webp': 85,  # Moderne, plus léger
                'gif': 80,   # Animations supportées
                'bmp': 60,   # Basique mais lourd
                'tiff': 50,  # Professionnel mais lourd
                'svg': 30,   # Vectoriel, support limité sur réseaux sociaux
                'ico': 20    # Icônes, non adapté
            }
            
            if ext in video_extensions:
                detected_type = 'video'
                confidence_score = video_extensions[ext]
                detection_method = f"extension_{ext}_conf{confidence_score}"
                print(f"✅ VIDÉO détectée par extension: {ext} (confiance: {confidence_score}%)")
            elif ext in image_extensions:
                detected_type = 'image'
                confidence_score = image_extensions[ext]
                detection_method = f"extension_{ext}_conf{confidence_score}"
                print(f"✅ IMAGE détectée par extension: {ext} (confiance: {confidence_score}%)")
        
        # Étape 2: Détection par magic bytes RENFORCÉE (signatures étendues)
        if not detected_type and len(content) >= 20:
            print(f"🔍 Analyse magic bytes RENFORCÉE des {min(64, len(content))} premiers bytes...")
            
            # Signatures vidéo ultra-complètes (spécialement MP4)
            video_signatures = [
                # MP4 signatures (problème principal identifié)
                (b'\x00\x00\x00\x18ftypmp4', 'mp4_standard'),          # MP4 standard
                (b'\x00\x00\x00\x20ftypmp4', 'mp4_variant'),           # MP4 variant
                (b'\x00\x00\x00\x1cftypisom', 'mp4_isom'),             # MP4 ISO Base Media
                (b'\x00\x00\x00\x20ftypisom', 'mp4_isom_variant'),     # MP4 ISO variant
                (b'\x00\x00\x00\x14ftyp', 'mp4_generic'),              # MP4 générique
                (b'\x00\x00\x00\x18ftyp', 'mp4_container'),            # MP4 container
                (b'\x00\x00\x00\x20ftyp', 'mp4_extended'),             # MP4 étendu
                (b'\x00\x00\x00\x24ftyp', 'mp4_large'),                # MP4 large header
                (b'ftypmp4', 'mp4_direct'),                             # MP4 signature directe
                (b'ftypisom', 'mp4_isom_direct'),                       # ISO direct
                (b'ftypM4V', 'mp4_m4v'),                                # M4V Apple
                (b'ftypM4A', 'mp4_m4a'),                                # M4A audio
                (b'ftypqt', 'mov_quicktime'),                           # QuickTime MOV
                
                # Autres formats vidéo
                (b'RIFF', 'riff_container'),                            # AVI/WebM (check further)
                (b'\x1aE\xdf\xa3', 'webm_mkv'),                        # WebM/MKV signature
                (b'FLV', 'flv_adobe'),                                  # Flash Video
                (b'\x30\x26\xb2\x75\x8e\x66\xcf\x11', 'wmv_asf'),     # Windows Media
                (b'\x00\x00\x01\xba', 'mpeg_ps'),                      # MPEG Program Stream
                (b'\x00\x00\x01\xb3', 'mpeg_video'),                   # MPEG Video
            ]
            
            # Signatures image complètes
            image_signatures = [
                (b'\xFF\xD8\xFF\xE0', 'jpeg_jfif'),                     # JPEG JFIF
                (b'\xFF\xD8\xFF\xE1', 'jpeg_exif'),                     # JPEG EXIF
                (b'\xFF\xD8\xFF\xDB', 'jpeg_quantization'),             # JPEG Quantization
                (b'\xFF\xD8\xFF', 'jpeg_generic'),                      # JPEG générique
                (b'\x89PNG\r\n\x1a\n', 'png_standard'),                 # PNG standard
                (b'GIF87a', 'gif_87a'),                                 # GIF 87a
                (b'GIF89a', 'gif_89a'),                                 # GIF 89a
                (b'RIFF', 'riff_webp_check'),                           # WebP dans RIFF
                (b'BM', 'bmp_windows'),                                 # Windows BMP
                (b'II\x2a\x00', 'tiff_little_endian'),                 # TIFF Little Endian
                (b'MM\x00\x2a', 'tiff_big_endian'),                    # TIFF Big Endian
                (b'WEBP', 'webp_direct'),                               # WebP direct
            ]
            
            # Test signatures vidéo avec vérifications approfondies
            for signature, format_name in video_signatures:
                signature_found = False
                if len(signature) <= len(content):
                    if content.startswith(signature):
                        signature_found = True
                    elif signature == b'RIFF' and content.startswith(b'RIFF'):
                        # Vérification spéciale RIFF (AVI vs WebP)
                        if len(content) >= 12:
                            if b'AVI ' in content[8:12]:
                                format_name = 'avi_riff'
                                signature_found = True
                            elif b'WEBM' in content[8:16] if len(content) >= 16 else False:
                                format_name = 'webm_riff'
                                signature_found = True
                
                if signature_found:
                    # Vérification additionnelle pour MP4 (atom structure)
                    if 'mp4' in format_name or 'mov' in format_name:
                        confidence_score = 95  # Haute confiance pour MP4
                        # Vérifier présence d'atoms MP4 typiques
                        if b'moov' in content[:1024] or b'mdat' in content[:1024]:
                            confidence_score = 99
                            print(f"🎯 STRUCTURE MP4 CONFIRMÉE (atoms moov/mdat détectés)")
                    else:
                        confidence_score = 85
                    
                    detected_type = 'video'
                    detection_method = f'magic_bytes_{format_name}_conf{confidence_score}'
                    print(f"✅ VIDÉO {format_name} détectée par magic bytes (confiance: {confidence_score}%)")
                    break
            
            # Test signatures image si pas de vidéo détectée
            if not detected_type:
                for signature, format_name in image_signatures:
                    signature_found = False
                    if len(signature) <= len(content) and content.startswith(signature):
                        if format_name == 'riff_webp_check':
                            # Vérifier que c'est bien WebP et pas vidéo
                            if len(content) >= 12 and b'WEBP' in content[8:12]:
                                format_name = 'webp_confirmed'
                                signature_found = True
                                confidence_score = 90
                        else:
                            signature_found = True
                            confidence_score = 90
                    
                    if signature_found:
                        detected_type = 'image'
                        detection_method = f'magic_bytes_{format_name}_conf{confidence_score}'
                        print(f"✅ IMAGE {format_name} détectée par magic bytes (confiance: {confidence_score}%)")
                        break
        
        # Étape 3: Analyse heuristique ULTRA-AVANCÉE avec patterns spécifiques
        if not detected_type and len(content) >= 200:
            print(f"🔍 Analyse heuristique ULTRA-AVANCÉE...")
            
            # Analyser jusqu'à 8KB pour patterns
            sample_size = min(8192, len(content))
            content_sample = content[:sample_size]
            
            # Patterns vidéo spécifiques (MP4/MOV focus)
            video_patterns = {
                b'ftyp': 25,    # File type atom (MP4/MOV)
                b'moov': 20,    # Movie atom (MP4/MOV)
                b'mdat': 15,    # Media data atom (MP4/MOV)
                b'mvhd': 15,    # Movie header atom
                b'trak': 10,    # Track atom
                b'mdhd': 10,    # Media header atom
                b'stbl': 8,     # Sample table atom
                b'stsd': 8,     # Sample description atom
                b'avc1': 12,    # H.264 video codec
                b'mp4v': 12,    # MPEG-4 video codec
                b'hvc1': 12,    # H.265 video codec
                b'vide': 5,     # Video track reference
                b'soun': 5,     # Sound track reference
            }
            
            # Patterns image spécifiques
            image_patterns = {
                b'JFIF': 20,    # JPEG File Interchange Format
                b'Exif': 15,    # Exchangeable image file format
                b'IHDR': 25,    # PNG Image Header
                b'PLTE': 10,    # PNG Palette
                b'tRNS': 8,     # PNG Transparency
                b'iCCP': 8,     # PNG ICC Profile
                b'gAMA': 5,     # PNG Gamma
                b'IDAT': 15,    # PNG Image Data
                b'IEND': 10,    # PNG Image End
            }
            
            # Calculer scores
            video_score = sum(weight for pattern, weight in video_patterns.items() if pattern in content_sample)
            image_score = sum(weight for pattern, weight in image_patterns.items() if pattern in content_sample)
            
            print(f"📊 Scores heuristiques: Vidéo={video_score}, Image={image_score}")
            
            if video_score > image_score and video_score >= 25:  # Seuil élevé pour vidéo
                detected_type = 'video'
                confidence_score = min(95, 60 + video_score)
                detection_method = f'heuristic_video_score_{video_score}_conf{confidence_score}'
                print(f"✅ VIDÉO détectée par heuristique avancée (score: {video_score}, confiance: {confidence_score}%)")
            elif image_score >= 15:  # Seuil pour image
                detected_type = 'image'
                confidence_score = min(90, 50 + image_score)
                detection_method = f'heuristic_image_score_{image_score}_conf{confidence_score}'
                print(f"✅ IMAGE détectée par heuristique avancée (score: {image_score}, confiance: {confidence_score}%)")
        
        # Étape 4: Analyse de taille intelligente avec seuils adaptatifs
        if not detected_type:
            file_size_mb = len(content) / (1024 * 1024)
            print(f"🔍 Analyse taille intelligente: {file_size_mb:.2f}MB")
            
            # Seuils adaptatifs basés sur l'expérience
            if file_size_mb > 50:
                # Très gros fichier = probablement vidéo
                detected_type = 'video'
                confidence_score = 80
                detection_method = f'size_very_large_{file_size_mb:.1f}MB_conf{confidence_score}'
                print(f"🎯 VIDÉO supposée (très gros fichier: {file_size_mb:.1f}MB)")
            elif file_size_mb > 15:
                # Gros fichier = probablement vidéo
                detected_type = 'video'
                confidence_score = 70
                detection_method = f'size_large_{file_size_mb:.1f}MB_conf{confidence_score}'
                print(f"🎯 VIDÉO supposée (gros fichier: {file_size_mb:.1f}MB)")
            elif file_size_mb > 5:
                # Fichier moyen = peut être vidéo courte ou image haute qualité
                detected_type = 'video'  # Privilégier vidéo car images > 5MB sont rares
                confidence_score = 60
                detection_method = f'size_medium_{file_size_mb:.1f}MB_conf{confidence_score}'
                print(f"🤔 VIDÉO supposée (fichier moyen: {file_size_mb:.1f}MB, confiance: {confidence_score}%)")
            else:
                # Petit fichier = probablement image
                detected_type = 'image'
                confidence_score = 70
                detection_method = f'size_small_{file_size_mb:.1f}MB_conf{confidence_score}'
                print(f"🖼️ IMAGE supposée (petit fichier: {file_size_mb:.1f}MB)")
        
        # Étape 5: Fallback ultime avec préférence vidéo (pour éviter erreurs MP4)
        if not detected_type:
            # Nouveau: privilégier vidéo en cas de doute (mieux vaut essayer vidéo que rater un MP4)
            detected_type = 'video'
            confidence_score = 40
            detection_method = 'ultimate_fallback_video_preference'
            print(f"⚠️ FALLBACK ULTIME: Traitement comme VIDÉO (pour éviter MP4 ratés)")
        
        print(f"🎯 DÉTECTION FINALE: {detected_type.upper()} (méthode: {detection_method}, confiance: {confidence_score}%)")
        
        # Log de debugging pour analyse post-mortem
        if confidence_score < 70:
            print(f"⚠️ CONFIANCE FAIBLE ({confidence_score}%) - Recommandé de vérifier manuellement")
            print(f"   Taille: {len(content)} bytes ({len(content)/1024/1024:.2f}MB)")
            print(f"   Premiers 32 bytes: {content[:32]}")
            print(f"   Filename: {filename}")
        
        return detected_type
        
    except Exception as e:
        print(f"❌ ERREUR DÉTECTION MÉDIA: {str(e)}")
        print(f"🔄 FALLBACK SÉCURISÉ: Traitement comme VIDÉO (préférence sécurisée)")
        return 'video'  # Changement: préférer vidéo en cas d'erreur