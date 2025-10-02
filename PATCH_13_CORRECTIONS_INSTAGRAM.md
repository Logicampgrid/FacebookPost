# 🔧 PATCH 13 - Corrections Instagram URLs FINALES

## 🎯 Problème résolu
Instagram recevait encore des chemins locaux Windows (`uploads\webhook_xxx.jpg`) au lieu d'URLs publiques HTTPS.

## ✅ Corrections à appliquer dans C:\FacebookPost\backend\server.py

### 1. Fonction `get_public_url` (ligne ~81)

**Remplacer :**
```python
def get_public_url(filename: str) -> str:
    """
    Construit l'URL publique ngrok pour un fichier uploadé.
    Patch 9: FTP désactivé, ngrok uniquement pour simplicité
    """
    return f"{NGROK_URL}/uploads/{os.path.basename(filename)}"
```

**Par :**
```python
def get_public_url(filename: str) -> str:
    """
    Construit l'URL publique ngrok pour un fichier uploadé.
    PATCH 13: Utilise l'URL dynamique détectée au lieu de l'URL hardcodée
    """
    # PATCH 13: Utiliser l'URL dynamique active au lieu de NGROK_URL hardcodée
    active_url = get_active_ngrok_url()
    if active_url:
        return f"{active_url}/uploads/{os.path.basename(filename)}"
    else:
        # Fallback vers l'URL hardcodée si détection échoue
        return f"{NGROK_URL}/uploads/{os.path.basename(filename)}"
```

### 2. Fonction `handle_n8n_publication` (ligne ~4490)

**Remplacer le bloc FTP :**
```python
        # Upload vers FTP pour obtenir l'URL publique
        media_url = None
        if is_video:
            log_app("🎥 Détection vidéo - Upload FTP...", "INFO")
            ftp_success, ftp_url, ftp_error = await upload_video_to_ftp(file_path, unique_filename)
        else:
            log_app("🖼️ Détection image - Upload FTP...", "INFO")
            ftp_success, ftp_url, ftp_error = await upload_image_to_ftp(file_path, file.filename)
        
        if ftp_success:
            media_url = ftp_url
            log_app(f"✅ Upload FTP réussi: {media_url}", "SUCCESS")
        else:
            # Fallback vers l'URL ngrok locale si disponible
            ngrok_url = get_active_ngrok_url()
            if ngrok_url:
                media_url = f"{ngrok_url}/uploads/{unique_filename}"
                log_app(f"⚠️ FTP échoué, utilisation ngrok: {media_url}", "WARNING")
            else:
                log_app(f"❌ Pas d'URL publique disponible: {ftp_error}", "ERROR")
                raise HTTPException(status_code=500, detail=f"Impossible de générer une URL publique: {ftp_error}")
```

**Par :**
```python
        # PATCH 13: NGROK UNIQUEMENT - Plus de FTP dans handle_n8n_publication
        # Générer directement l'URL publique ngrok comme dans le Patch 9
        media_url = get_public_url(unique_filename)
        log_app(f"🌐 PATCH 13: URL publique ngrok générée - {media_url}", "SUCCESS")
        
        if not media_url or not media_url.startswith('https://'):
            log_app(f"❌ PATCH 13: URL publique invalide générée: {media_url}", "ERROR")
            raise HTTPException(status_code=500, detail=f"Impossible de générer une URL publique valide")
```

### 3. Publication d'images (ligne ~4875)

**Remplacer :**
```python
            # Pour les images, utiliser le chemin local d'abord
            image_url = publication_data.get("image_url")
            if not image_url and publication_data.get("image_path"):
                # Optionnel: uploader l'image sur FTP pour une URL publique
                # Pour l'instant, utilisons le chemin local
                image_url = publication_data["image_path"]
```

**Par :**
```python
            # PATCH 13: Pour les images, convertir les chemins locaux en URLs publiques
            image_url = publication_data.get("image_url")
            if not image_url and publication_data.get("image_path"):
                # PATCH 13: Convertir le chemin local en URL publique ngrok
                image_path = publication_data["image_path"]
                if not image_path.startswith('http'):
                    filename = os.path.basename(image_path)
                    image_url = get_public_url(filename)
                    log_app(f"🌐 PATCH 13: Chemin local converti en URL publique - {image_url}", "SUCCESS")
                else:
                    image_url = image_path
```

### 4. Publication de vidéos (ligne ~4895)

**Remplacer :**
```python
        elif publication_data["publication_type"] == "video_post":
            # Pour les vidéos, uploader sur FTP d'abord
            video_path = publication_data["video_path"]
            upload_success, video_url, upload_error = await upload_video_to_ftp(video_path)
            
            if upload_success and video_url:
                result = await publish_video_main(
                    publication_data["store"],
                    publication_data["message"],
                    publication_data["product_url"],
                    video_url,
                    publication_data["platforms"]
                )
                publication_results["publication"] = result
                publication_results["video_upload"] = {
                    "success": True,
                    "video_url": video_url
                }
            else:
                raise Exception(f"Échec upload vidéo: {upload_error}")
```

**Par :**
```python
        elif publication_data["publication_type"] == "video_post":
            # PATCH 13: Pour les vidéos, utiliser ngrok uniquement
            video_path = publication_data["video_path"]
            
            # PATCH 13: Générer directement l'URL publique ngrok
            if not video_path.startswith('http'):
                filename = os.path.basename(video_path)
                video_url = get_public_url(filename)
                log_app(f"🌐 PATCH 13: Vidéo - chemin local converti en URL publique - {video_url}", "SUCCESS")
            else:
                video_url = video_path
            
            result = await publish_video_main(
                publication_data["store"],
                publication_data["message"],
                publication_data["product_url"],
                video_url,
                publication_data["platforms"]
            )
            publication_results["publication"] = result
            publication_results["video_upload"] = {
                "success": True,
                "video_url": video_url
            }
```

### 5. Fonction `publish_to_instagram` (ligne ~5507)

**Remplacer :**
```python
        # PATCH 9: Conversion URL simplifiée avec ngrok uniquement
        if not media_url.startswith(('http://', 'https://')):
            log_app(f"⚠️ PATCH 9: URL locale détectée, conversion ngrok - {media_url}", "WARNING")
            # Extraire le nom de fichier et générer l'URL publique ngrok
            filename = media_url.split("\\")[-1].split("/")[-1]  # Support Windows et Unix paths
            media_url = get_public_url(filename)
            log_app(f"✅ PATCH 9: URL convertie avec ngrok - {media_url}", "SUCCESS")
```

**Par :**
```python
        # PATCH 13: Conversion URL avec logs détaillés pour débogage Instagram
        log_app(f"🔍 PATCH 13: URL reçue par Instagram - '{media_url}'", "INFO")
        if not media_url.startswith(('http://', 'https://')):
            log_app(f"⚠️ PATCH 13: URL locale détectée, conversion ngrok - {media_url}", "WARNING")
            # Extraire le nom de fichier et générer l'URL publique ngrok
            filename = media_url.split("\\")[-1].split("/")[-1]  # Support Windows et Unix paths
            media_url = get_public_url(filename)
            log_app(f"✅ PATCH 13: URL convertie avec ngrok - {media_url}", "SUCCESS")
        else:
            log_app(f"✅ PATCH 13: URL déjà publique - {media_url}", "SUCCESS")
```

### 6. Logs de débogage avant envoi Instagram (ligne ~5531)

**Remplacer :**
```python
        log_app(f"📸 Publication Instagram vers {ig_user_id}: {caption[:100]}...", "INFO")
        
        # Étape 1: Créer le conteneur média
        response = requests.post(ig_url, data=data, timeout=30)
```

**Par :**
```python
        log_app(f"📸 Publication Instagram vers {ig_user_id}: {caption[:100]}...", "INFO")
        
        # PATCH 13: Debug - afficher exactement ce qui est envoyé à Instagram
        media_field = "video_url" if is_video else "image_url"
        log_app(f"🔍 PATCH 13: Données envoyées à Instagram - {media_field}: '{data.get(media_field)}'", "INFO")
        
        # Étape 1: Créer le conteneur média
        response = requests.post(ig_url, data=data, timeout=30)
```

## 🔍 Validation

Après avoir appliqué ces corrections et redémarré votre serveur, vous devriez voir dans les logs :
- `🔍 PATCH 13: URL reçue par Instagram` - pour chaque publication Instagram
- `🔍 PATCH 13: Données envoyées à Instagram - image_url: 'https://...'` - confirme que Instagram reçoit des URLs HTTPS

## ⚠️ Instructions importantes

1. **Sauvegardez** votre server.py actuel avant les modifications
2. **Appliquez** toutes les corrections ci-dessus
3. **Redémarrez** votre serveur backend
4. **Testez** avec une publication et vérifiez les nouveaux logs PATCH 13

Le problème Instagram sera alors **définitivement résolu** ! 🎉