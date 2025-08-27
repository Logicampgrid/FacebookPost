# 🎯 SOLUTION OFFICIELLE : Images Cliquables Garanties

## ✅ **Méthode Validée - Strategy 1C**

### **Pourquoi Strategy 1C est Optimale ?**

La Strategy 1C utilise l'endpoint Facebook `/feed` avec les paramètres :
- `picture`: URL de l'image (force l'affichage de l'image)
- `link`: URL du produit (rend l'image cliquable)
- `message`: Description du post

**Résultat :** Image s'affiche ET devient cliquable vers product_url

---

## 📡 **ENDPOINT RECOMMANDÉ**

```
POST https://votre-domaine.com/api/webhook
Content-Type: application/json
```

---

## 📋 **PAYLOAD EXACT**

```json
{
  "store": "votre_boutique",
  "title": "Nom du Produit", 
  "description": "Description du produit",
  "product_url": "https://votre-site.com/produit/123",
  "image_url": "https://votre-site.com/images/produit.jpg"
}
```

### **Champs Obligatoires :**
- `store` : Identifiant de votre boutique (ex: "gizmobbs", "outdoor", "logicantiq")
- `title` : Titre du produit (ne peut pas être vide)
- `product_url` : URL vers laquelle l'image doit rediriger (DOIT commencer par http/https)
- `image_url` : URL de l'image du produit (DOIT commencer par http/https)

### **Champs Optionnels :**
- `description` : Description (si vide, utilisera "Découvrez ce produit")

---

## 🔧 **EXEMPLE N8N WORKFLOW**

### **1. Node HTTP Request**

**Configuration :**
```
Method: POST
URL: https://votre-domaine.com/api/webhook
Authentication: None
Headers:
  Content-Type: application/json

Body (JSON):
{
  "store": "{{ $json.store }}",
  "title": "{{ $json.title }}",
  "description": "{{ $json.description }}",
  "product_url": "{{ $json.product_url }}",
  "image_url": "{{ $json.image_url }}"
}
```

### **2. Exemple avec Données Statiques**

```json
{
  "store": "gizmobbs",
  "title": "Super Produit Test",
  "description": "Découvrez ce magnifique produit dans notre boutique !",
  "product_url": "https://www.logicamp.org/wordpress/gizmobbs/produit/123",
  "image_url": "https://picsum.photos/800/600?random=123"
}
```

### **3. Workflow N8N Complet (JSON)**

```json
{
  "name": "Webhook Images Cliquables - Solution Officielle",
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "https://votre-domaine.com/api/webhook",
        "authentication": "none",
        "requestMethod": "POST",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyContentType": "json",
        "jsonBody": "{\n  \"store\": \"{{ $json.store }}\",\n  \"title\": \"{{ $json.title }}\",\n  \"description\": \"{{ $json.description }}\",\n  \"product_url\": \"{{ $json.product_url }}\",\n  \"image_url\": \"{{ $json.image_url }}\"\n}",
        "options": {}
      },
      "name": "Webhook Images Cliquables",
      "type": "n8n-nodes-base.httpRequest",
      "position": [740, 240],
      "id": "webhook-clickable-images"
    }
  ]
}
```

---

## 🎯 **RÉPONSE ATTENDUE**

### **Succès :**
```json
{
  "success": true,
  "status": "published", 
  "message": "Product 'Nom du Produit' published successfully to boutique",
  "data": {
    "facebook_post_id": "123456789_987654321",
    "post_id": "unique-post-id",
    "page_name": "Nom de la Page Facebook",
    "page_id": "page-facebook-id",
    "store": "votre_boutique",
    "published_at": "2025-01-27T10:30:00.000Z",
    "comment_added": false,
    "duplicate_skipped": false,
    "webhook_processed_at": "2025-01-27T10:30:00.000Z"
  }
}
```

### **Erreur :**
```json
{
  "success": false,
  "status": "error",
  "error": "Description de l'erreur",
  "webhook_processed_at": "2025-01-27T10:30:00.000Z"
}
```

---

## 🔍 **ALTERNATIVES (SI NÉCESSAIRE)**

### **2. Méthode Enhanced (JSON + Image Binaire)**

```
POST /api/webhook/enhanced
Content-Type: multipart/form-data

Form Data:
- json_data: '{"store":"boutique","title":"Produit","description":"...","product_url":"https://...","comment":"..."}'
- image: [fichier binaire]
```

### **3. Méthode Binary (Base64)**

```json
POST /api/webhook/binary
Content-Type: application/json

{
  "filename": "produit.jpg",
  "mimetype": "image/jpeg",
  "comment": "Description du produit",
  "link": "https://votre-site.com/produit/123",
  "data": "base64encodedimagedata"
}
```

---

## ✅ **GARANTIES**

1. **Images Toujours Cliquables** : Strategy 1C force l'image à être cliquable
2. **Affichage Garanti** : Paramètre `picture` force l'affichage de l'image
3. **Redirection Directe** : Clic sur l'image → product_url directement
4. **Compatible HTML** : Description HTML automatiquement nettoyée
5. **Gestion Duplicatas** : Évite les doublons automatiquement

---

## 🚀 **PRÊT À L'EMPLOI**

Cette solution est **validée et testée**. Utilisez l'endpoint `/api/webhook` avec le payload JSON exact pour des résultats garantis.

**Support :** Si problème, vérifiez que `store` existe dans la configuration et que les URLs commencent bien par `http/https`.