# 🚀 Guide du Webhook Enhancé N8N

## ✅ **Status : FONCTIONNEL**

Le nouveau webhook enhancé `/api/webhook/enhanced` est **opérationnel** et adapté à votre format N8N spécifique avec structure JSON/binary séparée.

## 🎯 **Nouveau Format Supporté**

Votre transformation N8N est maintenant supportée :

```javascript
return items.map(item => {
  return {
    json: {
      store: "ma-boutique",
      title: item.binary.data.fileName,
      description: "Découvrez ce produit dans notre boutique !",
      product_url: "https://www.logicamp.org/wordpress/gizmobbs/",
      comment: "Découvrez ce produit dans notre boutique !"
    },
    binary: {
      image: item.binary.data // met le binaire sous le champ "image"
    }
  };
});
```

## 📋 **Endpoints Disponibles**

### 1. **Webhook Enhancé (PRINCIPAL)**
```
POST https://smartprompt-7.preview.emergentagent.com/api/webhook/enhanced
Content-Type: multipart/form-data
```

**Structure multipart requise :**
- `json_data`: Chaîne JSON avec les métadonnées
- `image`: Fichier binaire image

### 2. **Informations du Webhook Enhancé**
```
GET https://smartprompt-7.preview.emergentagent.com/api/webhook/enhanced
```
Retourne la documentation, exemples, et configuration disponible.

## 🔧 **Configuration N8N**

### **Étape 1: Nœud de Transformation**
Utilisez votre transformation existante pour créer la structure JSON/binary :

```javascript
return items.map(item => {
  return {
    json: {
      store: "ma-boutique",
      title: item.binary.data.fileName,
      description: "Découvrez ce produit dans notre boutique !",
      product_url: "https://www.logicamp.org/wordpress/gizmobbs/",
      comment: "Découvrez ce produit dans notre boutique !"
    },
    binary: {
      image: item.binary.data
    }
  };
});
```

### **Étape 2: Nœud HTTP Request**
1. **Method**: `POST`
2. **URL**: `https://smartprompt-7.preview.emergentagent.com/api/webhook/enhanced`
3. **Body Type**: `Multipart-Form Data`
4. **Fields**:
   - `json_data`: `{{ JSON.stringify($json) }}`
   - `image`: `{{ $binary.image }}`

## 📊 **Structure des Données**

### **Données JSON (champ json_data)**
```json
{
  "store": "ma-boutique",
  "title": "nom_fichier.jpg",
  "description": "Découvrez ce produit dans notre boutique !",
  "product_url": "https://www.logicamp.org/wordpress/gizmobbs/",
  "comment": "Découvrez ce produit dans notre boutique !"
}
```

### **Données Binaires (champ image)**
- Fichier image binaire (JPEG, PNG, WebP, etc.)
- Taille max recommandée: 10MB
- Formats supportés: Tous formats d'image populaires

## 🎯 **Stores Disponibles**

| Store | Page Facebook | URL |
|-------|---------------|-----|
| `ma-boutique` | Le Berger Blanc Suisse | https://www.logicamp.org/wordpress/gizmobbs/ |
| `gizmobbs` | Le Berger Blanc Suisse | https://gizmobbs.com |
| `outdoor` | Logicamp Outdoor | https://logicampoutdoor.com |
| `logicantiq` | LogicAntiq | https://logicantiq.com |

## 🔄 **Processus de Publication**

1. **Réception**: N8N envoie JSON + image binaire
2. **Validation**: Vérification des champs requis et du store
3. **Sauvegarde**: Image enregistrée et optimisée localement
4. **Publication**: Post créé sur Facebook + Instagram (si disponible)
5. **Réponse**: Confirmation avec IDs de posts créés

## ✅ **Réponse de Succès**

```json
{
  "success": true,
  "status": "published",
  "message": "Product 'nom_fichier.jpg' published successfully to ma-boutique via enhanced webhook",
  "data": {
    "facebook_post_id": "102401876209415_668423672934157",
    "instagram_post_id": null,
    "post_id": "uuid-generated-id",
    "page_name": "Le Berger Blanc Suisse",
    "page_id": "102401876209415",
    "store": "ma-boutique",
    "published_at": "2025-08-17T13:47:26.479618",
    "duplicate_skipped": false,
    "enhanced_webhook": true,
    "original_filename": "nom_fichier.jpg",
    "generated_image_url": "https://smartprompt-7.preview.emergentagent.com/api/uploads/xxx.jpg",
    "comment_text": "Découvrez ce produit dans notre boutique !",
    "publication_summary": {
      "total_published": 1,
      "total_failed": 0
    }
  }
}
```

## 🚨 **Gestion des Erreurs**

### **Types d'Erreurs**
- `400`: Données manquantes ou invalides (JSON, image, champs requis)
- `500`: Erreur serveur ou problème de publication

### **Exemple d'Erreur**
```json
{
  "success": false,
  "status": "failed",
  "message": "Failed to process enhanced webhook: Invalid store 'invalid-store'",
  "error": {
    "type": "enhanced_webhook_processing_error",
    "details": "Invalid store 'invalid-store'. Available stores: outdoor, gizmobbs, gimobbs, logicantiq, ma-boutique",
    "timestamp": "2025-08-17T13:47:26.479618"
  }
}
```

## 🧪 **Tests et Validation**

### **Test Simple avec curl**
```bash
# Créer un test multipart
curl -X POST "https://smartprompt-7.preview.emergentagent.com/api/webhook/enhanced" \
  -F 'json_data={"store":"ma-boutique","title":"test.jpg","description":"Test produit","product_url":"https://www.logicamp.org/wordpress/gizmobbs/","comment":"Test comment"}' \
  -F 'image=@/path/to/test/image.jpg'
```

### **Vérification des Informations**
```bash
curl -X GET "https://smartprompt-7.preview.emergentagent.com/api/webhook/enhanced"
```

## 🔧 **Configuration N8N Détaillée**

### **Nœud HTTP Request - Configuration Complète**

1. **Parameters**:
   - **Method**: `POST`
   - **URL**: `https://smartprompt-7.preview.emergentagent.com/api/webhook/enhanced`
   - **Authentication**: None
   - **Send Body**: Yes
   - **Body Content Type**: `Multipart-Form Data`

2. **Body (Multipart-Form Data)**:
   ```
   Name: json_data
   Value: {{ JSON.stringify($json) }}
   
   Name: image  
   Value: {{ $binary.image }}
   Type: File
   ```

3. **Options**:
   - **Timeout**: 90000 (90 secondes)
   - **Retry**: 3 attempts
   - **Retry Wait**: 5000ms

## 📈 **Fonctionnalités Avancées**

✅ **Détection de Doublons**: Évite les publications répétées  
✅ **Optimisation d'Images**: Redimensionnement automatique pour les réseaux sociaux  
✅ **Multi-plateformes**: Publication simultanée Facebook + Instagram  
✅ **Gestion d'Erreurs**: Réponses détaillées pour debugging  
✅ **Logging**: Traces complètes pour monitoring  
✅ **Validation**: Contrôles stricts des données entrantes  

## 🎉 **Workflow N8N Complet Recommandé**

1. **Trigger** (File uploaded, Webhook, etc.)
2. **Read Binary File** (si nécessaire)
3. **Set** (préparation des données)
4. **Function** (transformation avec votre code)
5. **HTTP Request** (appel webhook enhancé)
6. **IF** (gestion succès/échec)
7. **Set** (logging/notification)

---

## ✅ **Résumé**

🎯 **Webhook adapté** à votre format N8N spécifique  
🎯 **Store "ma-boutique"** configuré et fonctionnel  
🎯 **Structure JSON/binary** supportée nativement  
🎯 **Publication automatique** Facebook + Instagram  
🎯 **Tests validés** et prêt pour production  

**Votre webhook enhancé est maintenant prêt pour l'intégration N8N !** 🚀