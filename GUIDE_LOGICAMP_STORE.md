# 📘 Guide d'Utilisation - Store Logicamp (PATCH 46)

## 🎯 Objectif
Publier des vidéos depuis N8N sur les pages Facebook et Instagram de Logicamp.

---

## ⚙️ Configuration

### Store Configuré
- **Nom**: `logicamp`
- **Page Facebook**: Logicamp (ID: `174450429258625`)
- **Instagram**: @logicamp.org (ID récupéré automatiquement)
- **Business Manager**: Didier Preud'homme (token partagé)

---

## 🚀 Première Utilisation

### Étape 1: Configuration Automatique de l'Instagram
Appelez cet endpoint pour récupérer automatiquement l'Instagram ID:

```bash
GET https://votre-backend.ngrok-free.app/api/stores/logicamp/setup-instagram
```

**Réponse attendue**:
```json
{
  "success": true,
  "store": "logicamp",
  "fb_page_id": "174450429258625",
  "ig_user_id": "XXXXXXXXXX",
  "message": "Instagram configuré avec succès pour Logicamp"
}
```

### Étape 2: Vérifier la Configuration
Le store est maintenant prêt à recevoir des publications !

---

## 📤 Publication depuis N8N

### Format du Webhook

**Endpoint**: `POST https://votre-backend.ngrok-free.app/api/webhook`

**Content-Type**: `multipart/form-data`

### Structure des Données

#### Pour les Images:
```json
{
  "json_data": {
    "store": "logicamp",
    "title": "Titre de votre publication",
    "url": "https://logicamp.org/produit/votre-produit",
    "description": "Description du produit"
  },
  "files": [fichier_image.jpg]
}
```

#### Pour les Vidéos:
```json
{
  "json_data": {
    "store": "logicamp",
    "title": "Titre de la vidéo",
    "url": "https://logicamp.org/produit/votre-produit",
    "description": "Description de la vidéo"
  },
  "files": [fichier_video.mp4]
}
```

---

## 🎬 Comportement Automatique

### Avec Média (Image/Vidéo):
- ✅ **Facebook**: Publication avec média
- ✅ **Instagram**: Publication automatique
  - Images → Post Instagram
  - Vidéos → Instagram Reels

### Sans Média (Texte uniquement):
- ✅ **Facebook**: Publication texte uniquement
- ❌ **Instagram**: Ignoré (média obligatoire)

---

## 📋 Formats Supportés

### Images
- JPG/JPEG
- PNG
- WEBP
- GIF

### Vidéos
- MP4 (recommandé)
- MOV
- Maximum Facebook: 10 GB
- Maximum Instagram Reels: 1 GB, 60 secondes

---

## 🔄 Workflow N8N Typique

```
1. Webhook Trigger (nouveau produit)
   ↓
2. Récupérer image/vidéo du produit
   ↓
3. HTTP Request (POST)
   • URL: https://votre-backend.ngrok-free.app/api/webhook
   • Method: POST
   • Body Type: Form-Data
   • Fields:
     - json_data: {"store": "logicamp", "title": "...", ...}
     - files: [fichier]
   ↓
4. Réponse immédiate (PATCH 45)
   {"status": "received", "processing": "background"}
   ↓
5. Publication en arrière-plan
   • Upload FTP
   • Publication Facebook
   • Publication Instagram
```

---

## ✅ Vérification des Publications

### Logs Serveur
```bash
# Publication réussie
✅ PATCH 46: Publication Facebook réussie - ID: XXXXXXXXX
✅ PATCH 46: Publication Instagram réussie - ID: XXXXXXXXX
```

### Base de Données MongoDB
```javascript
db.webhooks.find({
  "data.store": "logicamp",
  "status": "processed"
}).sort({timestamp: -1})
```

---

## 🛠️ Dépannage

### Erreur: "Aucun utilisateur connecté"
**Solution**: Connectez-vous d'abord avec Facebook dans l'interface web

### Erreur: "Aucun compte Instagram Business associé"
**Solution**: 
1. Allez sur votre Page Facebook
2. Paramètres → Instagram
3. Connectez votre compte Instagram Business

### Timeout N8N
**Solution**: Déjà résolu avec PATCH 45 - Réponse immédiate

### Publications Instagram échouent
**Vérifications**:
- Le compte Instagram est bien un compte Business
- Le compte est bien connecté à la page Facebook
- L'ID Instagram a été récupéré via `/api/stores/logicamp/setup-instagram`

---

## 📊 Stores Disponibles

| Store | Page Facebook | Instagram | Usage |
|-------|---------------|-----------|-------|
| `gizmobbs` | Le Berger Blanc Suisse | @logicamp_berger | Produits BBS |
| `logicantiq` | LogicAntiq | @logicantiq | Antiquités |
| `outdoor` | Logicamp Outdoor | @outdoor | Camping |
| `logicamp` | Logicamp | @logicamp.org | Vidéos générales |

---

## 🎯 Exemples Rapides

### Image Simple
```bash
curl -X POST https://votre-backend.ngrok-free.app/api/webhook \
  -F 'json_data={"store":"logicamp","title":"Nouveau produit","url":"https://logicamp.org/produit"}' \
  -F 'files=@image.jpg'
```

### Vidéo
```bash
curl -X POST https://votre-backend.ngrok-free.app/api/webhook \
  -F 'json_data={"store":"logicamp","title":"Vidéo démo","url":"https://logicamp.org/video"}' \
  -F 'files=@video.mp4'
```

---

## 📞 Support

En cas de problème:
1. Vérifier les logs du serveur backend
2. Consulter `/app/progress.md` pour l'historique des patches
3. Tester avec l'endpoint de diagnostic: `/api/debug/instagram-complete-diagnosis`

---

**Dernière mise à jour**: PATCH 46 - Store Logicamp configuré
**Date**: Session actuelle
**Crédits utilisés**: 6/10
