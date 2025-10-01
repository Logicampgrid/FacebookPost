# 🚀 Guide d'Intégration N8N - FacebookPost App

## 📋 Vue d'ensemble

Votre application FacebookPost a été **étendue avec succès** pour recevoir des données de produits depuis **n8n** et les publier automatiquement sur Facebook.

## ✅ Nouvelles Fonctionnalités Ajoutées

### 🛍️ **Endpoint Principal : `/api/publishProduct`**
- **Méthode** : `POST`
- **Content-Type** : `application/json`
- **Fonction** : Publie automatiquement un produit sur Facebook

### 🔧 **Endpoint de Configuration : `/api/publishProduct/config`**  
- **Méthode** : `GET`
- **Fonction** : Liste les utilisateurs et pages disponibles pour publication

### 🧪 **Endpoint de Test : `/api/publishProduct/test`**
- **Méthode** : `POST` 
- **Fonction** : Teste l'intégration sans publier réellement sur Facebook

## 📊 Structure des Données

### **Requête JSON (depuis n8n)**
```json
{
  "title": "Chaise design",
  "description": "Une chaise design moderne et confortable",
  "image_url": "https://mon-site.com/images/chaise.jpg",
  "product_url": "https://mon-site.com/produit/chaise-design",
  "user_id": "689c80feedee36b99f563ed0",  // Optionnel
  "page_id": "102401876209415",           // Optionnel  
  "api_key": "votre_api_key"              // Optionnel
}
```

### **Réponse de Succès**
```json
{
  "status": "success",
  "message": "Product 'Chaise design' published successfully to Facebook",
  "data": {
    "facebook_post_id": "102401876209415_123456789",
    "post_id": "uuid-generated-id",
    "page_name": "Le Berger Blanc Suisse",
    "page_id": "102401876209415",
    "user_name": "Didier Preud'homme",
    "published_at": "2025-08-13T15:30:00.000Z",
    "comment_added": true,
    "product_title": "Chaise design",
    "product_url": "https://mon-site.com/produit/chaise-design"
  }
}
```

## 🔧 Configuration N8N

### **1. Créer un Webhook N8N**

1. Ajoutez un nœud **HTTP Request** dans votre workflow n8n
2. Configurez les paramètres :
   - **Method** : `POST`
   - **URL** : `https://code-fixer-59.preview.emergentagent.com/api/publishProduct`
   - **Headers** : 
     ```json
     {
       "Content-Type": "application/json"
     }
     ```

### **2. Configuration du Body**

Dans le nœud HTTP Request, configurez le body avec les données de votre produit :

```json
{
  "title": "{{$json['product_title']}}",
  "description": "{{$json['product_description']}}",
  "image_url": "{{$json['product_image']}}",
  "product_url": "{{$json['product_link']}}",
  "page_id": "102401876209415"
}
```

### **3. Gestion des Erreurs**

Ajoutez un nœud **Error Handling** pour gérer les échecs :

```json
{
  "error_handling": {
    "continue_on_fail": true,
    "retry_on_fail": 3,
    "wait_between_tries": 5000
  }
}
```

## 🎯 Fonctionnement Détaillé

### **Processus de Publication**

1. **Réception des données** depuis n8n
2. **Validation** des champs requis
3. **Téléchargement et optimisation** de l'image produit
4. **Sélection automatique** de l'utilisateur et page Facebook
5. **Création du post** avec titre, description et image
6. **Publication sur Facebook** via l'API Graph
7. **Ajout d'un commentaire** avec le lien produit
8. **Sauvegarde** dans la base de données
9. **Retour de confirmation** à n8n

### **Contenu du Post Facebook**

Le post généré contiendra :
- ✅ **Titre du produit** en gras
- ✅ **Description** complète  
- ✅ **Image optimisée** pour Facebook
- ✅ **Commentaire automatique** avec lien vers le produit

## 🔑 Authentification & Sécurité

### **Utilisateurs Disponibles**

Pour voir les utilisateurs et pages disponibles :
```bash
GET https://code-fixer-59.preview.emergentagent.com/api/publishProduct/config
```

### **Sélection Automatique**

Si `user_id` et `page_id` ne sont pas spécifiés :
- 🔄 **Utilisateur** : Premier utilisateur avec des pages Facebook
- 🔄 **Page** : Première page Business Manager, sinon première page personnelle

### **Tokens Facebook**

⚠️ **Important** : Les tokens Facebook expirent régulièrement. Si vous obtenez une erreur `token expired` :

1. Connectez-vous à https://code-fixer-59.preview.emergentagent.com
2. Reconnectez-vous avec Facebook
3. Les nouveaux tokens seront automatiquement enregistrés

## 🧪 Tests & Debugging

### **Test Simple**
```bash
curl -X POST "https://code-fixer-59.preview.emergentagent.com/api/publishProduct/test" \
-H "Content-Type: application/json" \
-d '{
  "title": "Test Produit",
  "description": "Description du test",
  "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400",
  "product_url": "https://example.com/produit"
}'
```

### **Test Complet avec Publication**
```bash
curl -X POST "https://code-fixer-59.preview.emergentagent.com/api/publishProduct" \
-H "Content-Type: application/json" \
-d '{
  "title": "Chaise Design Premium",
  "description": "Découvrez notre nouvelle chaise design premium, alliant confort et esthétique moderne.",
  "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
  "product_url": "https://monsite.com/chaise-premium",
  "page_id": "102401876209415"
}'
```

## 📈 Monitoring & Logs

### **Logs Backend**
```bash
tail -f /var/log/supervisor/backend.out.log | grep "Product"
```

### **Messages de Succès**
- ✅ `Product 'X' published successfully`
- ✅ `Image downloaded and optimized`
- ✅ `Facebook post published: ID`
- ✅ `Product link comment added`

### **Messages d'Erreur Courants**
- ❌ `Token expired` → Reconnexion Facebook requise
- ❌ `Image download failed` → URL d'image invalide
- ❌ `No user found` → Aucun utilisateur configuré
- ❌ `Facebook API error` → Problème avec l'API Facebook

## 🚨 Gestion des Erreurs

### **Types d'Erreurs**

1. **`validation_error`** : Données manquantes ou invalides
2. **`image_download_error`** : Impossible de télécharger l'image
3. **`authentication_error`** : Utilisateur ou page introuvable  
4. **`facebook_api_error`** : Erreur de l'API Facebook
5. **`unknown_error`** : Erreur non classifiée

### **Codes de Réponse**

- **200** : Succès ✅
- **400** : Erreur de validation ⚠️
- **404** : Ressource non trouvée ❌
- **500** : Erreur serveur 💥

## 🎉 Exemple Complet N8N

### **Workflow N8N Recommandé**

1. **Trigger** (Webhook, Scheduled, etc.)
2. **Data Processing** (formatage des données produit)
3. **HTTP Request** → `/api/publishProduct`
4. **Success Handler** (traitement de la réponse)
5. **Error Handler** (gestion des échecs)

### **Configuration N8N Node**

```json
{
  "method": "POST",
  "url": "https://code-fixer-59.preview.emergentagent.com/api/publishProduct",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "title": "{{$json.title}}",
    "description": "{{$json.description}}", 
    "image_url": "{{$json.image}}",
    "product_url": "{{$json.url}}",
    "page_id": "102401876209415"
  },
  "options": {
    "timeout": 30000,
    "retry": {
      "enabled": true,
      "maxRetries": 3
    }
  }
}
```

## 📚 Ressources Supplémentaires

### **Endpoints Disponibles**
- `POST /api/publishProduct` - Publication produit
- `POST /api/publishProduct/test` - Test sans publication
- `GET /api/publishProduct/config` - Configuration disponible
- `GET /api/health` - Statut de l'application

### **Pages Facebook Disponibles**
- Le Berger Blanc Suisse (102401876209415)
- LogicAntiq (210654558802531)
- Autogpt-test1 (701770266356880)
- + 14 autres pages...

---

## 🎯 **Résumé**

✅ **Endpoint créé** : `/api/publishProduct`  
✅ **Intégration n8n** : Prête à utiliser  
✅ **Publication automatique** : Facebook avec image et lien  
✅ **Gestion d'erreurs** : Complète avec types d'erreurs  
✅ **Tests disponibles** : Mode test et production  
✅ **Documentation** : Guide complet d'utilisation  

**Votre application FacebookPost est maintenant prête pour l'intégration n8n !** 🚀