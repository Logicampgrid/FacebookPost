# 🎥 Test Publication Vidéo Logicamp - PATCH 47

## Configuration validée ✅
- Store: `logicamp`
- Page Facebook: Logicamp (ID: 174450429258625, 373 fans)
- Instagram: @logicamporg (ID: 17841461492706552, 96 followers)
- Token: Partagé avec gizmobbs (Business Manager Didier Preud'homme)

## Exemple de webhook N8N pour vidéo

### Format multipart/form-data (recommandé)

```bash
curl -X POST "http://localhost:8001/api/webhook" \
  -H "Content-Type: multipart/form-data" \
  -F "store=logicamp" \
  -F "title=Découvrez notre boutique Logicamp !" \
  -F "url=https://www.logicamp.org/wordpress/" \
  -F "description=Vidéo de présentation de nos produits" \
  -F "image=@/chemin/vers/video.mp4"
```

### Ce qui va se passer:

1. **Upload FTP** (automatique) ✅
   - Vidéo uploadée sur `logicamp.org/wordpress/uploads/`
   - URL publique générée: `https://logicamp.org/wordpress/uploads/webhook_xxx.mp4`

2. **Publication Facebook** ✅
   - Endpoint: `/v18.0/174450429258625/videos`
   - Upload direct du fichier vidéo
   - Description: Titre + URL + Description

3. **Publication Instagram Reels** ✅
   - Création container: `/v18.0/17841461492706552/media`
   - Publication: `/v18.0/17841461492706552/media_publish`
   - Caption: Titre + URL + Description

### Résultat attendu:

```json
{
  "success": true,
  "status": "published",
  "store": "logicamp",
  "platforms": ["facebook", "instagram"],
  "data": {
    "facebook_post_id": "174450429258625_xxx",
    "instagram_post_id": "18xxxxx",
    "video_url": "https://logicamp.org/wordpress/uploads/webhook_xxx.mp4"
  }
}
```

## Vérification sur les réseaux sociaux:

- **Facebook**: https://www.facebook.com/174450429258625
- **Instagram**: https://www.instagram.com/logicamporg/

## Limitations:

- **Taille max**: 1 GB pour Instagram, 10 GB pour Facebook
- **Durée max**: 60 secondes pour Instagram Reels, 15 minutes pour Facebook
- **Formats supportés**: MP4, MOV
- **Délai**: Traitement en arrière-plan (PATCH 45) - réponse immédiate

## Dépannage:

Si erreur "Configuration manquante":
```bash
# Recharger les variables d'environnement
cd /app/backend
python setup_logicamp_instagram.py

# Redémarrer le serveur (si nécessaire)
sudo supervisorctl restart backend
```

Si vidéo ne s'affiche pas sur Instagram:
- Vérifier que l'URL est publique et accessible depuis internet
- Vérifier que le format est MP4 (H.264 vidéo, AAC audio)
- Vérifier que la durée est < 60 secondes pour Reels

## Notes PATCH 47:

✅ Store logicamp maintenant identique aux autres stores (gizmobbs, logicantiq, outdoor)
✅ Pas besoin de configuration spéciale pour les vidéos vs images
✅ Upload FTP automatique pour rendre les URLs publiques
✅ Publications Facebook + Instagram simultanées
✅ Token partagé = moins de maintenance
