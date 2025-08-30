# Guide Configuration N8N - Webhook Gizmobbs Multipart

## Configuration HTTP Request N8N

### 1. Node HTTP Request - Configuration générale
```
Method: POST
URL: https://feed-link-update.preview.emergentagent.com/api/webhook
Authentication: None
```

### 2. Body Configuration
```
Body Content Type: Form-Data
```

### 3. Champs Form-Data requis

#### Champ json_data (string)
```json
{
  "store": "gizmobbs",
  "title": "{{ $json.title }}",
  "url": "{{ $json.product_url }}",
  "description": "{{ $json.description }}"
}
```

#### Champ binaire (image OU video)
- **Nom du champ**: `image` (pour images) OU `video` (pour vidéos)
- **Type**: Binary Data
- **Source**: `{{ $binary.data }}`

### 4. Headers requis
```
Content-Type: multipart/form-data
```
*Note: N8N ajoutera automatiquement ce header*

## Exemple pratique N8N

### Configuration complète node HTTP Request:

1. **Method**: `POST`
2. **URL**: `https://feed-link-update.preview.emergentagent.com/api/webhook`
3. **Body**: `Form-Data`
4. **Form Fields**:
   - `json_data` (String): 
     ```json
     {"store": "gizmobbs", "title": "{{ $json.title }}", "url": "{{ $json.product_url }}", "description": "{{ $json.description }}"}
     ```
   - `image` (Binary): `{{ $binary.data }}` (si c'est une image)
   - `video` (Binary): `{{ $binary.data }}` (si c'est une vidéo)

### Workflow exemple:

```
[RSS/API] → [Transform Data] → [HTTP Request Gizmobbs]
```

#### Node Transform Data (avant HTTP Request):
```javascript
// Exemple de transformation
const items = $input.all();

return items.map(item => {
  return {
    json: {
      title: item.json.title || 'Produit sans titre',
      product_url: item.json.link || item.json.url,
      description: item.json.description || item.json.content || 'Découvrez ce produit'
    },
    binary: item.binary // Contient l'image ou la vidéo
  };
});
```

## Types de médias supportés

### Images acceptées:
- `.jpg`, `.jpeg`, `.png`, `.webp`
- Taille max recommandée: 10MB

### Vidéos acceptées:
- `.mp4`, `.mov`, `.avi`, `.webm`
- Taille max recommandée: 50MB

## Comportements automatiques

### Pour les images (champ `image`):
- ✅ Image affichée dans l'interface
- ✅ **Cliquable** vers l'URL du produit (json_data.url)
- ✅ Publication automatique sur Facebook/Instagram

### Pour les vidéos (champ `video`):
- ✅ Vidéo avec lecteur intégré
- ✅ **Commentaire affiché** (json_data.description)
- ✅ Lien vers le produit dans le commentaire
- ✅ Publication automatique sur Facebook/Instagram

## Réponses Webhook

### Succès:
```json
{
  "success": true,
  "status": "published",
  "message": "N8N multipart content 'Titre' published successfully",
  "media_type": "image|video",
  "data": {
    "facebook_post_id": "...",
    "instagram_post_id": "...",
    "page_name": "...",
    "published_at": "..."
  }
}
```

### Erreur:
```json
{
  "success": false,
  "status": "failed",
  "message": "Error description",
  "error": {
    "type": "validation_error",
    "details": "...",
    "timestamp": "..."
  }
}
```

## Validation des données

### Champs requis dans json_data:
- ✅ `store`: "gizmobbs"
- ✅ `title`: Titre non vide
- ✅ `url`: URL valide (http/https)
- ✅ `description`: Description (peut être vide)

### Fichier requis:
- ✅ Soit `image` soit `video` (pas les deux)
- ✅ Type MIME valide
- ✅ Taille raisonnable

## Dépannage

### Erreur 400 - Bad Request
- Vérifiez que `json_data` contient un JSON valide
- Vérifiez qu'un seul fichier (`image` OU `video`) est envoyé
- Vérifiez que tous les champs requis sont présents

### Erreur 422 - Unprocessable Entity  
- Vérifiez le type MIME du fichier
- Vérifiez que l'URL est valide (commence par http/https)

### Images/vidéos ne s'affichent pas
- Vérifiez que le fichier a été correctement uploadé
- Vérifiez les logs backend pour les erreurs de traitement
- Testez l'URL générée manuellement

## Test manuel avec curl

```bash
curl -X POST "https://feed-link-update.preview.emergentagent.com/api/webhook" \
  -F 'json_data={"store":"gizmobbs","title":"Test Produit","url":"https://exemple.com","description":"Ceci est un test"}' \
  -F 'image=@test_image.jpg'
```

## Support

En cas de problème:
1. Vérifiez les logs N8N
2. Testez avec curl d'abord
3. Vérifiez l'interface webhook dans l'application
4. Contactez le support technique avec les détails de l'erreur

---

*Dernière mise à jour: Configuration optimisée pour Gizmobbs avec support multipart/form-data complet*