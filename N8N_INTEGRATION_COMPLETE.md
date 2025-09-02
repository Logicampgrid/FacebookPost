# 🚀 Intégration N8N - FacebookPost Application

## ✅ **Status : FONCTIONNEL**

L'endpoint `/api/publishProduct` est **opérationnel** et prêt pour l'intégration avec n8n.

## 📋 **Endpoints disponibles**

### 1. **Publication de produits (PRINCIPAL)**
```
POST https://ecu-corrector.preview.emergentagent.com/api/publishProduct
```

**Payload JSON requis :**
```json
{
  "title": "Nom du produit",
  "description": "Description détaillée du produit",
  "image_url": "https://example.com/image.jpg",
  "product_url": "https://example.com/produit/page",
  "user_id": "optional_user_id",
  "page_id": "optional_page_id",
  "api_key": "optional_api_key"
}
```

**Réponse de succès :**
```json
{
  "status": "success",
  "message": "Product 'Nom du produit' published successfully to Facebook",
  "data": {
    "facebook_post_id": "123456789_987654321",
    "post_id": "uuid-post-id",
    "page_name": "Ma Page Facebook",
    "page_id": "page_id",
    "user_name": "Nom Utilisateur",
    "published_at": "2025-08-13T15:46:25.165831",
    "comment_added": true,
    "product_title": "Nom du produit",
    "product_url": "https://example.com/produit/page"
  }
}
```

### 2. **Test de publication (POUR TESTS)**
```
POST https://ecu-corrector.preview.emergentagent.com/api/publishProduct/test
```
Même payload que l'endpoint principal, mais simule la publication sans poster sur Facebook.

### 3. **Configuration disponible**
```
GET https://ecu-corrector.preview.emergentagent.com/api/publishProduct/config
```
Retourne la liste des utilisateurs et pages Facebook disponibles.

### 4. **Gestion des utilisateurs de test**
```
POST https://ecu-corrector.preview.emergentagent.com/api/publishProduct/setup-test-user
DELETE https://ecu-corrector.preview.emergentagent.com/api/publishProduct/cleanup-test-user
```

## 🔧 **Configuration N8N**

### Étape 1 : Créer un webhook HTTP Request
1. **URL** : `https://ecu-corrector.preview.emergentagent.com/api/publishProduct`
2. **Méthode** : `POST`
3. **Headers** :
   ```
   Content-Type: application/json
   ```

### Étape 2 : Configurer le body JSON
```json
{
  "title": "{{ $json.title }}",
  "description": "{{ $json.description }}",
  "image_url": "{{ $json.image_url }}",
  "product_url": "{{ $json.product_url }}"
}
```

### Étape 3 : Exemple complet avec curl
```bash
curl -X POST "https://ecu-corrector.preview.emergentagent.com/api/publishProduct" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Chaise design premium",
    "description": "Une magnifique chaise design moderne, confortable et élégante. Parfaite pour votre salon ou bureau.",
    "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800",
    "product_url": "https://example.com/produit/chaise-design-premium"
  }'
```

## 📊 **Fonctionnalités**

✅ **Validation automatique** des champs requis  
✅ **Téléchargement et optimisation** automatique des images  
✅ **Publication sur Facebook** avec API Graph  
✅ **Ajout automatique d'un commentaire** avec le lien produit  
✅ **Gestion d'erreurs** détaillée  
✅ **Mode test** pour développement  
✅ **Support multi-utilisateurs et multi-pages**  

## 🎯 **Ce qui se passe lors d'une publication**

1. **Validation** : Vérification des champs requis
2. **Téléchargement image** : Récupération et optimisation de l'image produit
3. **Création du post** : Combinaison titre + description
4. **Publication Facebook** : Post sur la page Facebook sélectionnée
5. **Ajout commentaire** : Lien produit ajouté en commentaire
6. **Sauvegarde** : Enregistrement en base de données
7. **Réponse** : Confirmation avec ID du post Facebook

## ⚠️ **Gestion d'erreurs**

L'API retourne des codes d'erreur HTTP appropriés :

- `400` : Données manquantes ou invalides
- `404` : Utilisateur ou page non trouvé
- `500` : Erreur serveur ou API Facebook

**Exemple d'erreur :**
```json
{
  "detail": {
    "error": "Product title is required",
    "error_type": "validation_error",
    "product_title": "Unknown",
    "timestamp": "2025-08-13T15:46:25.165831"
  }
}
```

## 🔐 **Authentification**

Pour utiliser l'endpoint avec de vraies pages Facebook :
1. Un utilisateur doit se connecter via l'interface web
2. Autoriser l'accès aux pages Facebook
3. L'endpoint utilisera automatiquement la première page disponible
4. Ou spécifier `user_id` et `page_id` pour cibler une page spécifique

## 🧪 **Mode Test Intégré**

L'application détecte automatiquement les tokens de test et simule les publications Facebook sans les publier réellement. Parfait pour le développement !

## 📝 **Logs et Monitoring**

Tous les appels sont loggés côté serveur avec :
- Détails de la requête
- Statut de téléchargement d'image
- Résultat de publication Facebook
- Erreurs éventuelles

## 🚀 **Prêt pour production**

L'endpoint est entièrement fonctionnel et prêt pour une utilisation en production avec n8n !