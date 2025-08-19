# 🚀 Intégration N8N - FacebookPost Application (MISE À JOUR)

## ✅ **Nouvelles Fonctionnalités Ajoutées**

### 🏪 **Sélection Dynamique des Pages Facebook**

L'application peut maintenant publier automatiquement sur **3 pages spécifiques** selon le type de boutique :

- **🏕️ LogicampOutdoor** (`outdoor`) - Produits outdoor et camping
- **📱 Gizmobbs** (`gizmobbs`) - Produits technologiques  
- **🏛️ LogicAntiq** (`logicantiq`) - Antiquités et objets vintage

### 📊 **Historique des Publications Webhook**

- Interface dédiée pour consulter toutes les publications reçues via webhook
- Filtrage par type de boutique
- Statut de publication et ajout de commentaires
- Liens directs vers les produits et posts Facebook

---

## 🛍️ **Utilisation N8N avec Sélection de Page**

### **Endpoint Principal**
```
POST https://extend-url.preview.emergentagent.com/api/publishProduct
```

### **Payload JSON avec Sélection de Boutique**
```json
{
  "title": "Tente 4 places premium",
  "description": "Tente familiale 4 places avec double toit imperméable. Parfaite pour vos aventures en pleine nature !",
  "image_url": "https://monsite.com/images/tente-4-places.jpg",
  "product_url": "https://logicampoutdoor.com/produit/tente-4-places-premium",
  "shop_type": "outdoor"
}
```

### **Types de Boutiques Disponibles**

| `shop_type` | Page Facebook | Boutique WooCommerce |
|-------------|---------------|---------------------|
| `outdoor` | LogicampOutdoor | https://logicampoutdoor.com |
| `gizmobbs` | Gizmobbs | https://gizmobbs.com |
| `logicantiq` | LogicAntiq | https://logicantiq.com |

---

## 🔧 **Configuration N8N - Exemples par Boutique**

### **1. Produits Outdoor (LogicampOutdoor)**

**Node HTTP Request :**
```json
{
  "method": "POST",
  "url": "https://extend-url.preview.emergentagent.com/api/publishProduct",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "title": "{{$json.product_name}}",
    "description": "🏕️ {{$json.product_description}}\n\n✨ Parfait pour vos aventures outdoor !",
    "image_url": "{{$json.product_image}}",
    "product_url": "{{$json.product_url}}",
    "shop_type": "outdoor"
  }
}
```

### **2. Produits Technologiques (Gizmobbs)**

**Node HTTP Request :**
```json
{
  "method": "POST", 
  "url": "https://extend-url.preview.emergentagent.com/api/publishProduct",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "title": "{{$json.product_name}}",
    "description": "📱 {{$json.product_description}}\n\n🚀 Technologie de pointe au meilleur prix !",
    "image_url": "{{$json.product_image}}",
    "product_url": "{{$json.product_url}}",
    "shop_type": "gizmobbs"
  }
}
```

### **3. Antiquités (LogicAntiq)**

**Node HTTP Request :**
```json
{
  "method": "POST",
  "url": "https://extend-url.preview.emergentagent.com/api/publishProduct", 
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "title": "{{$json.product_name}}",
    "description": "🏛️ {{$json.product_description}}\n\n⭐ Pièce authentique et unique !",
    "image_url": "{{$json.product_image}}",
    "product_url": "{{$json.product_url}}",
    "shop_type": "logicantiq"
  }
}
```

---

## 📈 **Workflows N8N Avancés**

### **Workflow 1 : Publication selon Catégorie Produit**

```javascript
// Node: Product Category Detection
const product = $input.item.json;
let shopType = "logicantiq"; // par défaut

// Logique de détection automatique
if (product.categories.includes("outdoor") || 
    product.categories.includes("camping") ||
    product.categories.includes("sport")) {
  shopType = "outdoor";
} else if (product.categories.includes("tech") ||
           product.categories.includes("electronique") ||
           product.categories.includes("smartphone")) {
  shopType = "gizmobbs";
} else if (product.categories.includes("antique") ||
           product.categories.includes("vintage") ||
           product.categories.includes("collection")) {
  shopType = "logicantiq";
}

return [{
  json: {
    ...product,
    determined_shop_type: shopType
  }
}];
```

### **Workflow 2 : Publication Programmée Multi-Boutiques**

```javascript
// Node: Daily Product Selection
const products = [
  {
    title: "Sac à dos randonnée 50L",
    description: "Sac technique pour longues randonnées",
    shop_type: "outdoor",
    image_url: "https://logicampoutdoor.com/images/sac-50l.jpg",
    product_url: "https://logicampoutdoor.com/sac-randonnee-50l"
  },
  {
    title: "Écouteurs Bluetooth Premium",
    description: "Son haute qualité avec réduction de bruit",
    shop_type: "gizmobbs", 
    image_url: "https://gizmobbs.com/images/ecouteurs-premium.jpg",
    product_url: "https://gizmobbs.com/ecouteurs-bluetooth-premium"
  },
  {
    title: "Vase en porcelaine XIXe",
    description: "Magnifique vase d'époque en parfait état",
    shop_type: "logicantiq",
    image_url: "https://logicantiq.com/images/vase-porcelaine.jpg", 
    product_url: "https://logicantiq.com/vase-porcelaine-xixe"
  }
];

// Sélection aléatoire
const randomProduct = products[Math.floor(Math.random() * products.length)];
return [{ json: randomProduct }];
```

---

## 🎯 **Gestion d'Erreurs et Fallback**

### **Si `shop_type` non spécifié ou invalide :**
- ✅ L'application utilise la **première page disponible** (comportement actuel)
- ✅ La publication fonctionne normalement

### **Si la page spécifique n'existe pas :**
- ⚠️ L'application cherche par **nom de page** (ex: "LogicAntiq")
- ✅ **Fallback** vers la première page disponible  
- 📝 **Log détaillé** de la sélection de page

### **Node N8N de Validation :**
```javascript
// Valider shop_type avant publication
const validShopTypes = ["outdoor", "gizmobbs", "logicantiq"];
const item = $input.item.json;

if (!item.shop_type || !validShopTypes.includes(item.shop_type)) {
  console.warn(`shop_type invalide: ${item.shop_type}, utilisation de logicantiq par défaut`);
  item.shop_type = "logicantiq";
}

return [{ json: item }];
```

---

## 📊 **Monitoring et Historique**

### **Endpoint Historique**
```
GET https://extend-url.preview.emergentagent.com/api/webhook-history?limit=100
```

**Réponse :**
```json
{
  "status": "success",
  "data": {
    "webhook_posts": [
      {
        "id": "post-uuid",
        "title": "Tente 4 places premium",
        "shop_type": "outdoor",
        "page_name": "LogicampOutdoor", 
        "status": "published",
        "comment_added": true,
        "received_at": "2025-08-13T16:30:00Z",
        "facebook_post_id": "page_id_post_id"
      }
    ],
    "shop_mapping": {
      "outdoor": {
        "name": "LogicampOutdoor",
        "woocommerce_url": "https://logicampoutdoor.com"
      }
    }
  }
}
```

### **Interface Web**
- 🎯 **Onglet "Historique Webhook"** dans l'application
- 📊 **Statistiques par boutique**
- 🔄 **Actualisation en temps réel**
- 🔗 **Liens directs vers produits et posts Facebook**

---

## 🧪 **Tests et Validation**

### **Test Simple par Boutique :**

**Outdoor :**
```bash
curl -X POST "https://extend-url.preview.emergentagent.com/api/publishProduct/test" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tente 2 places ultra-légère",
    "description": "Tente de randonnée ultra-légère pour backpackers",
    "image_url": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800",
    "product_url": "https://logicampoutdoor.com/tente-2-places",
    "shop_type": "outdoor"
  }'
```

**Gizmobbs :**
```bash
curl -X POST "https://extend-url.preview.emergentagent.com/api/publishProduct/test" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Smartphone 5G 128GB",
    "description": "Dernier smartphone avec 5G et appareil photo pro",
    "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800",
    "product_url": "https://gizmobbs.com/smartphone-5g-128gb",
    "shop_type": "gizmobbs"
  }'
```

**LogicAntiq :**
```bash
curl -X POST "https://extend-url.preview.emergentagent.com/api/publishProduct/test" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Commode Louis XVI",
    "description": "Authentique commode d'époque Louis XVI restaurée",
    "image_url": "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=800",
    "product_url": "https://logicantiq.com/commode-louis-xvi",
    "shop_type": "logicantiq"
  }'
```

---

## 📚 **Récapitulatif des Améliorations**

### ✅ **Nouvelles Fonctionnalités**
1. **Sélection dynamique des pages** via `shop_type`
2. **Support 3 boutiques** : Outdoor, Gizmobbs, LogicAntiq  
3. **Historique des publications webhook** dans l'interface
4. **API d'historique** pour monitoring externe
5. **Gestion d'erreurs avancée** avec fallback
6. **Documentation complète** avec exemples par boutique

### ✅ **Compatibilité**
- ✅ **100% compatible** avec l'existant
- ✅ **Publication manuelle** conservée
- ✅ **Endpoints existants** inchangés
- ✅ **Fallback automatique** si shop_type non spécifié

### ✅ **Prêt pour Production**
- 🚀 **Déployé et testé**
- 📖 **Documentation complète** 
- 🔧 **Interface utilisateur** mise à jour
- 📊 **Monitoring intégré**

---

## 🎉 **Votre Application est Prête !**

✨ **L'application FacebookPost peut maintenant :**
- 🎯 Publier automatiquement sur la bonne page selon le type de produit
- 📊 Afficher l'historique des publications webhook
- 🔄 Conserver toutes les fonctionnalités manuelles existantes
- 📖 Fournir une documentation complète pour N8N

**🚀 Intégration N8N améliorée et prête pour vos 3 boutiques !**