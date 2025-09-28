# 📨 Documentation Webhook Publication Facebook/Instagram

## 🎯 Objectif

Nouvel endpoint webhook intégré dans l'application existante permettant de publier automatiquement du contenu sur Facebook et Instagram via formulaire POST.

## 🚀 Endpoint

```
POST /api/webhook/publish
```

## 📋 Paramètres Requis

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `store` | FormData | Store à utiliser (gizmobbs, logicantiq, outdoor) | `gizmobbs` |
| `title` | FormData | Titre de la publication | `"Nouveau produit disponible"` |
| `url` | FormData | URL du produit/article | `"https://monsite.com/produit"` |
| `description` | FormData | Description détaillée | `"Description complète du produit"` |
| `file` | File | Image ou vidéo à publier | `fichier.jpg` |

## 🔧 Exemple d'utilisation

### Curl
```bash
curl -X POST http://localhost:8001/api/webhook/publish \
  -F "store=gizmobbs" \
  -F "title=Nouveau Produit Fantastique" \
  -F "url=https://boutique.com/produit-123" \
  -F "description=Découvrez notre nouveau produit avec des caractéristiques exceptionnelles!" \
  -F "file=@image_produit.jpg" \
  -H "Content-Type: multipart/form-data"
```

### Python
```python
import requests

url = "http://localhost:8001/api/webhook/publish"
data = {
    "store": "gizmobbs",
    "title": "Nouveau Produit Fantastique",
    "url": "https://boutique.com/produit-123",
    "description": "Découvrez notre nouveau produit!"
}
files = {
    "file": ("produit.jpg", open("produit.jpg", "rb"), "image/jpeg")
}

response = requests.post(url, data=data, files=files)
print(response.json())
```

### Node.js / JavaScript
```javascript
const FormData = require('form-data');
const fs = require('fs');

const form = new FormData();
form.append('store', 'gizmobbs');
form.append('title', 'Nouveau Produit Fantastique');
form.append('url', 'https://boutique.com/produit-123');
form.append('description', 'Découvrez notre nouveau produit!');
form.append('file', fs.createReadStream('produit.jpg'));

fetch('http://localhost:8001/api/webhook/publish', {
    method: 'POST',
    body: form
}).then(response => response.json())
  .then(data => console.log(data));
```

## 📊 Réponse

### Succès
```json
{
  "success": true,
  "store": "gizmobbs",
  "store_name": "Le Berger Blanc Suisse",
  "file_info": {
    "filename": "webhook_abc123_1234567890.jpg",
    "original_filename": "produit.jpg",
    "content_type": "image/jpeg",
    "size": 245760,
    "is_video": false,
    "media_url": "https://exemple.ngrok-free.app/uploads/webhook_abc123_1234567890.jpg"
  },
  "publications": {
    "facebook": {
      "success": true,
      "response": {
        "id": "123456789_987654321"
      }
    },
    "instagram": {
      "success": true,
      "response": {
        "id": "987654321123456789"
      }
    }
  },
  "message": "Publications réussies sur Facebook et Instagram"
}
```

### Erreur
```json
{
  "success": false,
  "store": "gizmobbs",
  "message": "Échec des publications sur les deux plateformes",
  "publications": {
    "facebook": {
      "success": false,
      "error": "Erreur détaillée Facebook"
    },
    "instagram": {
      "success": false,
      "error": "Erreur détaillée Instagram"
    }
  }
}
```

## 🏪 Stores Disponibles

| Store | Nom | Configuration |
|-------|-----|---------------|
| `gizmobbs` | Le Berger Blanc Suisse | Facebook + Instagram |
| `logicantiq` | LogicAntiq | Facebook + Instagram |
| `outdoor` | Logicamp Outdoor | Facebook + Instagram |

## 🔒 Configuration Requise

### Tokens d'accès
- Tokens Facebook valides dans les variables d'environnement
- Configuration STORES dans server.py mise à jour
- Permissions de publication sur les pages/comptes Instagram

### Infrastructure
- Serveur ngrok actif pour URLs publiques (recommandé)
- Configuration FTP pour upload des médias (fallback ngrok local)
- MongoDB pour logs (optionnel)

## 🎥 Types de fichiers supportés

### Images
- `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- Taille maximum recommandée: 10MB

### Vidéos
- `.mp4`, `.mov`, `.avi`, `.wmv`  
- Taille maximum Facebook: 10GB
- Taille maximum Instagram: 1GB
- Durée maximum Instagram: 60 secondes

## ⚡ Fonctionnalités Avancées

### Upload FTP automatique
- Les fichiers sont uploadés automatiquement vers le serveur FTP configuré
- URL publique générée automatiquement pour compatibilité Instagram
- Fallback vers ngrok local si FTP indisponible

### Détection automatique du type
- Images: Publication via `/photos` endpoint
- Vidéos: Publication via `/videos` (Facebook) et `/media` (Instagram Reels)

### Gestion d'erreurs robuste
- Erreurs détaillées pour chaque plateforme
- Succès partiel supporté (une plateforme réussie)
- Logs complets pour debugging

## 📱 Intégration avec N8N / Zapier

L'endpoint est compatible avec les plateformes d'automatisation :

### N8N
1. Utiliser le node "HTTP Request"
2. Method: POST
3. URL: `http://votre-serveur:8001/api/webhook/publish`
4. Body Type: Form-Data
5. Ajouter les paramètres requis

### Zapier
1. Utiliser "Webhooks by Zapier"
2. Action: POST
3. URL: endpoint webhook
4. Payload Type: form

## 🔧 Maintenance

### Logs
Les logs sont visibles dans la console du serveur FastAPI avec des icônes distinctifs :
- 📥 Réception webhook
- 📋 Configuration store
- 💾 Sauvegarde fichier
- 📤 Upload FTP
- 📱 Publication Facebook  
- 📸 Publication Instagram

### Troubleshooting
1. **Token expiré**: Renouveler les tokens dans les variables d'environnement
2. **Upload FTP échoué**: Vérifier la configuration FTP ou utiliser ngrok
3. **Fichier rejeté**: Vérifier le format et la taille du fichier
4. **Store introuvable**: Utiliser un des stores configurés (gizmobbs, logicantiq, outdoor)

## 📞 Support

Pour toute question ou problème :
1. Vérifier les logs du serveur
2. Tester avec l'endpoint `/api/test-gizmobbs` 
3. Valider la configuration FTP avec `/api/test-ftp`

---

**✅ Endpoint intégré avec succès dans l'infrastructure existante !**