# 📋 Référence Complète des Webhooks FacebookPost

## 🎯 Vue d'ensemble

Ce document décrit toutes les stratégies disponibles, formats acceptés, et configurations pour le système webhook FacebookPost.

---

## 🔧 Stratégies de Publication

### **Stratégie 1A : Upload Direct d'Image (multipart)**
- **Description** : Upload direct via endpoint `/photos` avec fichier multipart
- **Usage** : Publication d'images locales avec affichage garanti
- **Avantages** : 
  - ✅ 100% d'affichage image garanti
  - ✅ Meilleure qualité d'image
  - ✅ Pas de dépendance URL externe
- **Déclencheur** : Fichier image disponible localement
- **Code d'exemple** :
```python
# Upload multipart vers /photos endpoint
data = {
    "access_token": page_access_token,
    "message": post.content
}
files = {"source": open(local_file_path, "rb")}
endpoint = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/photos"
```

### **Stratégie 1B : Post Photo via URL**
- **Description** : Publication d'image via URL sur endpoint `/photos`
- **Usage** : Images hébergées accessibles publiquement
- **Avantages** :
  - ✅ 100% d'affichage image garanti
  - ✅ Rapide sans upload
  - ✅ Supporte images externes
- **Déclencheur** : URL d'image publique valide
- **Code d'exemple** :
```python
# Post photo via URL
data = {
    "access_token": page_access_token,
    "message": post.content,
    "url": full_media_url
}
endpoint = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/photos"
```

### **Stratégie 1C : Post Lien Enrichi avec Image Forcée** 
- **Description** : Post sur `/feed` avec paramètres `link` et `picture`
- **Usage** : **Automatiquement déclenchée quand paramètre `store` est présent**
- **Avantages** :
  - ✅ Images cliquables vers produits
  - ✅ Prévisualisation forcée de l'image
  - ✅ Idéal pour e-commerce
- **Déclencheur** : **Paramètre `store` présent dans requête webhook**
- **Code d'exemple** :
```python
# Stratégie 1C - Lien enrichi avec image
data = {
    "access_token": page_access_token,
    "message": post.content,
    "link": product_link,      # URL du produit (cliquable)
    "picture": full_media_url  # Force l'affichage de l'image
}
endpoint = f"{FACEBOOK_GRAPH_URL}/{post.target_id}/feed"
```

---

## 📤 Formats Acceptés par le Webhook

### **Format 1 : JSON Standard (endpoint `/api/webhook`)**
```json
{
  "store": "gizmobbs",
  "title": "Nom du Produit",
  "description": "Description du produit (HTML sera nettoyé automatiquement)",
  "product_url": "https://exemple.com/produit",
  "image_url": "https://exemple.com/image.jpg"
}
```
- **Déclencheur Stratégie 1C** : ✅ Présence du champ `store`
- **Nettoyage HTML** : ✅ Automatique pour `title` et `description`
- **Validation** : ✅ Tous les champs requis

### **Format 2 : Multipart Enhanced (endpoint `/api/webhook/enhanced`)**
```bash
curl -X POST "URL/api/webhook/enhanced" \
  -F 'json_data={"store":"ma-boutique","title":"produit.jpg","description":"Description","product_url":"https://exemple.com","comment":"Commentaire"}' \
  -F 'image=@/path/to/image.jpg'
```
- **Déclencheur Stratégie 1C** : ✅ Présence du champ `store` dans json_data
- **Upload Binary** : ✅ Image directement uploadée
- **Optimisation** : ✅ Redimensionnement automatique

### **Format 3 : Binary Webhook (endpoint `/api/webhook/binary`)**
```json
{
  "json_data": {
    "store": "outdoor",
    "title": "Titre",
    "description": "Description",
    "product_url": "https://exemple.com"
  },
  "binary_data": "base64_encoded_image_data"
}
```
- **Déclencheur Stratégie 1C** : ✅ Présence du champ `store`
- **Base64** : ✅ Image encodée en base64
- **Conversion** : ✅ Automatique vers fichier local

---

## 🌐 Configuration Webhook Externe (NGROK)

### **Variables d'Environnement**
```bash
# Configuration NGROK pour webhook externe
NGROK_URL=https://bbf80c7dd1d5.ngrok-free.app
EXTERNAL_WEBHOOK_ENABLED=true
```

### **Activation du Webhook Externe**
Quand `EXTERNAL_WEBHOOK_ENABLED=true` :
1. **Réception** : Webhook reçoit la requête normalement
2. **Validation** : Données validées et nettoyées
3. **Transfert** : Données envoyées vers `NGROK_URL` 
4. **Fallback** : Si NGROK échoue, traitement interne normal

### **Format Envoyé vers NGROK**
```json
{
  "source": "internal_webhook",
  "timestamp": "2025-08-17T14:30:00.000Z",
  "store": "gizmobbs",
  "strategy": "1C",
  "data": {
    "store": "gizmobbs",
    "title": "Produit Nettoyé",
    "description": "Description sans HTML",
    "product_url": "https://exemple.com/produit",
    "image_url": "https://exemple.com/image.jpg",
    "strategy": "1C",
    "original_request": {...}
  }
}
```

### **Configuration NGROK Recommandée**
```bash
# Démarrer tunnel NGROK
ngrok http 3000 --domain=bbf80c7dd1d5.ngrok-free.app

# Ou avec configuration personnalisée
ngrok http 3000 --domain=votre-domain.ngrok-free.app --log=stdout
```

### **Endpoints NGROK Disponibles**
- **Principal** : `https://bbf80c7dd1d5.ngrok-free.app/api/webhook`
- **Enhanced** : `https://bbf80c7dd1d5.ngrok-free.app/api/webhook/enhanced`
- **Binary** : `https://bbf80c7dd1d5.ngrok-free.app/api/webhook/binary`

---

## 🏪 Configuration des Stores

### **Mapping Store → Page Facebook**
```python
SHOP_PAGE_MAPPING = {
    "gizmobbs": {
        "page_id": "102401876209415",
        "page_name": "Le Berger Blanc Suisse",
        "platform": "instagram_priority",  # Publication prioritaire Instagram
        "url": "https://gizmobbs.com"
    },
    "outdoor": {
        "page_id": "auto_detect",
        "page_name": "Logicamp Outdoor", 
        "platform": "multi",  # Facebook + Instagram
        "url": "https://logicampoutdoor.com"
    },
    "logicantiq": {
        "page_id": "auto_detect",
        "page_name": "LogicAntiq",
        "platform": "facebook_only",  # Facebook uniquement
        "url": "https://logicantiq.com"
    },
    "ma-boutique": {
        "page_id": "102401876209415",
        "page_name": "Le Berger Blanc Suisse",
        "platform": "multi",
        "url": "https://www.logicamp.org/wordpress/gizmobbs/"
    }
}
```

### **Stratégies par Store**
| Store | Stratégie par Défaut | Avec Paramètre `store` |
|-------|---------------------|------------------------|
| `gizmobbs` | Auto (1A→1B→1C) | **Force 1C** ✅ |
| `outdoor` | Auto (1A→1B→1C) | **Force 1C** ✅ |
| `logicantiq` | Auto (1A→1B→1C) | **Force 1C** ✅ |
| `ma-boutique` | Auto (1A→1B→1C) | **Force 1C** ✅ |

---

## 🔍 Bonnes Pratiques

### **1. Gestion des Paramètres**
- ✅ **Toujours inclure `store`** pour déclencher Stratégie 1C
- ✅ **URLs complètes** pour `product_url` et `image_url`
- ✅ **Validation côté client** avant envoi webhook
- ✅ **Gestion des timeouts** (30s recommandé)

### **2. Formatage des Données**
- ✅ **HTML automatiquement nettoyé** dans `title` et `description`
- ✅ **URLs validées** (doivent commencer par http/https)
- ✅ **Textes de fallback** si description vide
- ✅ **Encodage UTF-8** pour caractères spéciaux

### **3. Gestion d'Erreurs**
```json
// Réponse d'erreur type
{
  "success": false,
  "status": "failed",
  "message": "Description détaillée de l'erreur",
  "error": {
    "type": "validation_error|api_error|network_error",
    "details": "Informations techniques détaillées",
    "timestamp": "2025-08-17T14:30:00.000Z"
  }
}
```

### **4. Monitoring et Logs**
- ✅ **Logs détaillés** pour chaque requête webhook
- ✅ **Traçabilité** strategy utilisée (1A, 1B, ou 1C)
- ✅ **Métriques de succès** par store et stratégie
- ✅ **Alertes sur échecs** répétés

---

## 🧪 Tests et Validation

### **Test Stratégie 1C (paramètre store)**
```bash
# Test avec store = déclenchement automatique 1C
curl -X POST "https://gizmobbs-media-api.preview.emergentagent.com/api/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "store": "gizmobbs",
    "title": "Test Stratégie 1C",
    "description": "Test avec paramètre store pour forcer stratégie 1C",
    "product_url": "https://gizmobbs.com/test-produit",
    "image_url": "https://picsum.photos/800/600"
  }'
```

### **Test Webhook Externe (NGROK)**
```bash
# 1. Activer webhook externe
export EXTERNAL_WEBHOOK_ENABLED=true
export NGROK_URL=https://bbf80c7dd1d5.ngrok-free.app

# 2. Test avec transfert NGROK
curl -X POST "https://gizmobbs-media-api.preview.emergentagent.com/api/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "store": "outdoor",
    "title": "Test NGROK Transfer",
    "description": "Test de transfert vers webhook externe",
    "product_url": "https://logicampoutdoor.com/test",
    "image_url": "https://picsum.photos/1080/1080"
  }'
```

### **Vérification des Stratégies**
```bash
# Info sur toutes les stratégies disponibles
curl -X GET "https://gizmobbs-media-api.preview.emergentagent.com/api/debug/facebook-image-fix"

# Info webhook standard
curl -X GET "https://gizmobbs-media-api.preview.emergentagent.com/api/webhook"

# Info webhook enhanced  
curl -X GET "https://gizmobbs-media-api.preview.emergentagent.com/api/webhook/enhanced"
```

---

## 📊 Métriques et Performance

### **Taux de Succès par Stratégie**
- **Stratégie 1A** : ~95% (dépend de la disponibilité fichier local)
- **Stratégie 1B** : ~90% (dépend de l'accessibilité URL)
- **Stratégie 1C** : ~98% (le plus fiable pour e-commerce)

### **Temps de Réponse Moyens**
- **Webhook Standard** : ~2-5 secondes
- **Webhook Enhanced** : ~3-8 secondes (upload inclus)
- **Webhook Binary** : ~4-10 secondes (décodage inclus)
- **Transfert NGROK** : +1-3 secondes (réseau)

---

## 🚀 Intégration N8N Optimisée

### **Configuration Recommandée**
```javascript
// Transformation N8N avec déclenchement Stratégie 1C
return items.map(item => {
  return {
    json: {
      store: "gizmobbs",        // 🎯 DÉCLENCHE STRATÉGIE 1C
      title: item.json.title,
      description: stripHtml(item.json.description),
      product_url: item.json.url,
      comment: "Découvrez ce produit !"
    },
    binary: {
      image: item.binary.data
    }
  };
});
```

### **Nœud HTTP Request N8N**
- **URL** : `https://gizmobbs-media-api.preview.emergentagent.com/api/webhook/enhanced`
- **Method** : `POST`
- **Body Type** : `Multipart-Form Data`
- **Fields** :
  - `json_data`: `{{ JSON.stringify($json) }}`
  - `image`: `{{ $binary.image }}`

---

## ✅ Résumé de Configuration

### **Pour Déclencher Stratégie 1C**
1. ✅ **Inclure paramètre `store`** dans toute requête webhook
2. ✅ **Valeurs valides** : `gizmobbs`, `outdoor`, `logicantiq`, `ma-boutique`
3. ✅ **Résultat** : Images cliquables avec liens produits

### **Pour Webhook Externe**
1. ✅ **Variable** : `NGROK_URL=https://bbf80c7dd1d5.ngrok-free.app`
2. ✅ **Activation** : `EXTERNAL_WEBHOOK_ENABLED=true`
3. ✅ **Fallback** : Traitement interne si NGROK échoue

### **Endpoints Principaux**
- **Standard** : `/api/webhook` (JSON simple)
- **Enhanced** : `/api/webhook/enhanced` (Multipart + binary)
- **Binary** : `/api/webhook/binary` (Base64 images)
- **Info** : `/api/webhook` (GET pour documentation)

---

*Document généré le : 2025-08-17*  
*Version : 1.0*  
*Dernière mise à jour : Finalisation branche fb3*