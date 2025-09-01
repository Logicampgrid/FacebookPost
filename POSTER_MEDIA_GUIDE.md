# 📱 Guide d'utilisation de poster_media() - Publication automatique Instagram

## 🎯 Vue d'ensemble

La fonctionnalité `poster_media()` permet de publier automatiquement toutes les images et vidéos présentes dans le dossier `C:/gizmobbs/download` sur Instagram, en passant par un upload FTP intermédiaire.

## 📋 Fonctionnalités

- ✅ **Détection automatique** des formats supportés (images et vidéos)
- ✅ **Conversion WebP → JPEG** pour compatibilité Instagram  
- ✅ **Upload FTP** vers votre serveur (logicamp.org)
- ✅ **Publication Instagram** via l'API Graph
- ✅ **Gestion des erreurs** et logs détaillés
- ✅ **Archivage automatique** dans le dossier "processed"

## 🔧 Configuration requise

### 1. Variables d'environnement (.env)

Ajoutez ces variables dans `/app/backend/.env` :

```env
# Configuration pour poster_media() - Publication automatique Instagram
# Variables FTP pour upload des médias
FTP_HOST=logicamp.org
FTP_PORT=21
FTP_USER=logi
FTP_PASS=logi
FTP_UPLOAD_DIR=/wordpress/upload/

# Variables Instagram API Graph
# Remplacez par vos vrais tokens
ACCESS_TOKEN=VOTRE_ACCESS_TOKEN_INSTAGRAM
IG_USER_ID=VOTRE_IG_USER_ID

# Dossier de téléchargement automatique (Windows)
AUTO_DOWNLOAD_DIR=C:/gizmobbs/download
```

### 2. Obtenir vos tokens Instagram

#### ACCESS_TOKEN
1. Allez sur [Facebook for Developers](https://developers.facebook.com/)
2. Sélectionnez votre application
3. Outils > Explorateur d'API Graph
4. Sélectionnez votre page Facebook connectée à Instagram
5. Générez un token avec les permissions : `instagram_basic`, `instagram_content_publish`

#### IG_USER_ID  
1. Dans l'Explorateur d'API Graph, utilisez l'endpoint :
   ```
   GET /{page-id}?fields=instagram_business_account
   ```
2. L'ID retourné est votre `IG_USER_ID`

## 📁 Structure des dossiers

```
C:/gizmobbs/
├── download/           # Dossier source (vos fichiers à publier)
│   ├── image1.jpg      # ✅ Sera publié
│   ├── video1.mp4      # ✅ Sera publié  
│   ├── photo.webp      # ✅ Sera converti puis publié
│   └── document.pdf    # ❌ Ignoré (format non supporté)
└── processed/          # Créé automatiquement après publication
    ├── image1.jpg      # Fichiers traités avec succès
    └── video1.mp4
```

## 🎬 Formats supportés

### Images
- `.jpg`, `.jpeg` → Publication directe
- `.png` → Publication directe  
- `.webp` → Conversion automatique en JPEG
- `.gif` → Publication directe (si supporté par Instagram)

### Vidéos
- `.mp4` → Publication en tant que Reels
- `.mov` → Publication en tant que Reels

## 🚀 Utilisation

### Méthode 1 : Via endpoint API (Recommandée)

```bash
# Vérifier le statut et la configuration
curl -X GET "http://localhost:8001/api/poster-media/status"

# Déclencher la publication manuelle
curl -X POST "http://localhost:8001/api/poster-media"
```

### Méthode 2 : Via interface web

Accédez à votre interface de gestion et utilisez le bouton "Publier les médias".

## 📊 Processus de publication

1. **🔍 Parcours** du dossier `C:/gizmobbs/download`
2. **📋 Filtrage** des fichiers valides (extensions supportées)
3. **🔄 Conversion** WebP en JPEG si nécessaire
4. **📤 Upload FTP** vers `logicamp.org/wordpress/upload/`
5. **📱 Publication Instagram** via API Graph avec caption automatique
6. **📁 Archivage** dans le dossier `processed`

## 📝 Exemple de réponse API

```json
{
  "success": true,
  "timestamp": "2025-09-01T21:30:00.000000",
  "source_directory": "C:/gizmobbs/download",
  "ftp_server": "logicamp.org:21",
  "instagram_account": "VOTRE_IG_USER_ID",
  "result": {
    "success": true,
    "stats": {
      "files_found": 5,
      "files_processed": 3,
      "files_uploaded": 3,
      "files_published": 3,
      "files_ignored": 2,
      "files_failed": 0,
      "errors": []
    },
    "message": "Publication terminée: 3/3 fichiers publiés"
  }
}
```

## 🐛 Résolution des problèmes

### Erreur : "Dossier source non trouvé: C:/gizmobbs/download"
```bash
# Créer le dossier manuellement
mkdir -p "C:/gizmobbs/download"
```

### Erreur : "ACCESS_TOKEN ou IG_USER_ID non configurés"
- Vérifiez que vous avez remplacé `VOTRE_ACCESS_TOKEN_ICI` et `VOTRE_IG_USER_ID_ICI` dans le fichier `.env`
- Redémarrez le serveur après modification : `sudo supervisorctl restart backend`

### Erreur FTP
```bash
# Tester la connexion FTP manuellement
ftp logicamp.org
# login: logi
# password: logi
```

### Erreur publication Instagram
- Vérifiez que votre token n'a pas expiré
- Vérifiez les permissions `instagram_basic` et `instagram_content_publish`
- Vérifiez que le compte est bien un compte Business Instagram

## 📈 Logs et monitoring

Les logs sont affichés en temps réel avec des icônes pour faciliter le suivi :

```
ℹ️ [21:30:15] [POSTER_MEDIA] Parcours du dossier: C:/gizmobbs/download
✅ [21:30:16] [POSTER_MEDIA] Upload FTP réussi: image1.jpg
📱 [21:30:17] [POSTER_MEDIA] Publication Instagram réussie: 18234567890
✅ [21:30:17] [POSTER_MEDIA] Fichier déplacé vers processed: image1.jpg
```

## 🔒 Sécurité

- Les credentials FTP sont stockés dans le fichier `.env` (non versionné)
- Les tokens Instagram sont protégés par les variables d'environnement
- Les fichiers sont traités localement avant upload
- Aucune donnée sensible n'est loggée

## 🚨 Points importants

1. **Tokens Instagram** : Doivent être renouvelés périodiquement
2. **Permissions** : Votre application Facebook doit avoir les permissions Instagram approuvées
3. **Format vidéo** : Instagram préfère MP4 avec codec H.264
4. **Taille limite** : Respectez les limites Instagram (images: 8MB, vidéos: 100MB)
5. **Doublons** : Les fichiers avec le même nom seront renommés automatiquement

## 📞 Support

En cas de problème :
1. Vérifiez les logs du serveur : `tail -f /var/log/supervisor/backend*.log`
2. Testez la configuration : `GET /api/poster-media/status`
3. Vérifiez la connectivité FTP et Instagram API

---

**Date de création** : 1er septembre 2025  
**Version** : 1.0  
**Compatibilité** : Windows/Linux avec serveur FastAPI