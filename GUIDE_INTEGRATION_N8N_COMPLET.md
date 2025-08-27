# 🎯 GUIDE COMPLET : Intégration N8N pour Images Cliquables

## 📋 **RÉSUMÉ EXÉCUTIF**

**Solution Validée :** Webhook multipart/form-data garantissant des images cliquables à 100%

**Endpoint :** `POST /api/webhook`  
**Format :** `multipart/form-data`  
**Test :** ✅ Validé en conditions réelles  
**Résultat :** Image cliquable → redirection vers product_url  

---

## 🚀 **INTÉGRATION N8N : ÉTAPE PAR ÉTAPE**

### **Étape 1 : Configuration du Workflow**

1. **Créer un nouveau workflow N8N**
2. **Ajouter un node "Webhook" comme déclencheur**
3. **Ajouter un node "HTTP Request" pour le webhook**
4. **Configurer la logique de traitement**

### **Étape 2 : Configuration du Node HTTP Request**

**Paramètres principaux :**
```
Method: POST
URL: https://votre-domaine.com/api/webhook
Authentication: None
Send Binary Data: ✅ Activé
Content Type: multipart-form-data
```

**Body Parameters :**
```
Name: json_data
Type: Expression
Value: {{ JSON.stringify({
  "title": $json.title,
  "description": $json.description, 
  "url": $json.product_url,
  "store": $json.store
}) }}
```

**Binary Data :**
```
Property Name: image
Input Binary Field: data (ou le nom du champ contenant l'image)
```

### **Étape 3 : Mapping des Données**

**Données d'entrée typiques :**
```json
{
  "title": "Nom du produit",
  "description": "Description du produit",
  "product_url": "https://votre-site.com/produit/123",
  "image_url": "https://votre-site.com/image.jpg",
  "store": "gizmobbs"
}
```

**Transformation N8N :**
1. **Télécharger l'image** depuis `image_url` (node HTTP Request)
2. **Préparer les métadonnées** JSON (node Set)
3. **Envoyer via multipart** (node HTTP Request multipart)

---

## 🔧 **EXEMPLES DE CODE N8N**

### **Expression pour json_data :**
```javascript
{{
  JSON.stringify({
    "title": $json.title || "Produit",
    "description": $json.description || "Découvrez ce produit",
    "url": $json.product_url || $json.url,
    "store": $json.store || "gizmobbs"
  })
}}
```

### **Téléchargement d'image :**
```javascript
// Node HTTP Request pour télécharger l'image
Method: GET
URL: {{ $json.image_url }}
Response Format: File
```

### **Validation des données :**
```javascript
// Expression de validation
{{
  $json.title && $json.product_url && $json.image_url 
    ? "valid" 
    : "missing_required_fields"
}}
```

---

## 📊 **WORKFLOW COMPLET RECOMMANDÉ**

```
1. [Webhook Trigger] 
   ↓
2. [Validate Input] 
   ↓
3. [Download Image] (HTTP Request GET)
   ↓
4. [Prepare JSON Data] (Set node)
   ↓
5. [Multipart Webhook] (HTTP Request POST multipart)
   ↓
6. [Handle Response] (IF node)
   ↓
7. [Success/Error Response]
```

---

## ⚙️ **CONFIGURATION DÉTAILLÉE**

### **Node 1: Webhook Trigger**
```json
{
  "httpMethod": "POST",
  "path": "product-webhook",
  "responseMode": "onReceived"
}
```

### **Node 2: Download Image**
```json
{
  "method": "GET",
  "url": "={{ $json.image_url }}",
  "responseFormat": "file"
}
```

### **Node 3: Prepare Data**
```json
{
  "values": {
    "string": [
      {"name": "title", "value": "={{ $json.title }}"},
      {"name": "description", "value": "={{ $json.description }}"},
      {"name": "url", "value": "={{ $json.product_url }}"},
      {"name": "store", "value": "={{ $json.store }}"}
    ]
  }
}
```

### **Node 4: Multipart Webhook**
```json
{
  "method": "POST",
  "url": "https://votre-domaine.com/api/webhook",
  "sendBinaryData": true,
  "contentType": "multipart-form-data",
  "bodyParameters": {
    "parameters": [
      {
        "name": "json_data",
        "value": "={{ JSON.stringify({title: $json.title, description: $json.description, url: $json.url, store: $json.store}) }}"
      }
    ]
  }
}
```

---

## 🎯 **DONNÉES D'EXEMPLE POUR TESTS**

### **Payload d'entrée N8N :**
```json
{
  "title": "🧪 Test Image Cliquable",
  "description": "Ceci est un test d'image cliquable pour vérifier la redirection",
  "product_url": "https://www.logicamp.org/wordpress/gizmobbs/produit/test",
  "image_url": "https://picsum.photos/800/600?random=123",
  "store": "gizmobbs"
}
```

### **Réponse attendue :**
```json
{
  "status": "success",
  "message": "Webhook processed successfully",
  "data": {
    "image_filename": "webhook_abc123.jpg",
    "publication_results": [{
      "facebook_post_id": "123456789_987654321",
      "page_name": "Le Berger Blanc Suisse",
      "status": "success"
    }]
  }
}
```

---

## 🚨 **GESTION D'ERREURS**

### **Erreurs Communes :**

1. **Image manquante :**
```json
{"detail": [{"loc": ["body", "image"], "msg": "Field required"}]}
```

2. **JSON invalide :**
```json
{"detail": "Invalid JSON format: ..."}
```

3. **Store invalide :**
```json
{"detail": "Invalid store 'xyz'. Available stores: gizmobbs, outdoor, logicantiq"}
```

### **Gestion dans N8N :**
```javascript
// Dans un node IF après le webhook
{{ $json.status === "success" }}
// Branche True: Succès
// Branche False: Erreur
```

---

## ✅ **CHECKLIST DE VALIDATION**

- [ ] **URL correcte** : Endpoint webhook configuré
- [ ] **Multipart activé** : Content-Type = multipart/form-data  
- [ ] **Binary data** : Image téléchargée et passée en binaire
- [ ] **JSON valide** : Champs title, description, url, store présents
- [ ] **Store existant** : Utiliser "gizmobbs", "outdoor", "logicantiq" ou "ma-boutique"
- [ ] **URLs absolues** : product_url commence par http/https
- [ ] **Test complet** : Vérifier la publication Facebook réelle

---

## 🎉 **RÉSULTAT FINAL**

Une fois configuré correctement, le workflow N8N :

1. ✅ **Reçoit** les données produit via webhook
2. ✅ **Télécharge** l'image depuis image_url  
3. ✅ **Envoie** image + métadonnées en multipart
4. ✅ **Publie** sur Facebook avec image cliquable
5. ✅ **Retourne** l'ID du post Facebook créé

**L'image publiée sera automatiquement cliquable et redirigera vers product_url !**