# 🎯 Guide Spécifique : Webhook Gizmobbs → @logicamp_berger

## ✅ CONFIGURATION RÉALISÉE

Votre système a été **OPTIMISÉ** pour publier automatiquement sur **@logicamp_berger** via webhook avec `shop_type: "gizmobbs"`.

### 📋 Configuration Instagram @logicamp_berger

```
📱 Instagram: @logicamp_berger
🏢 Business Manager ID: 1715327795564432
🛍️ Shop Type: "gizmobbs"
🎯 Plateforme: Instagram PRIORITAIRE
🔗 URL: https://www.instagram.com/logicamp_berger/
```

---

## 🚀 UTILISATION WEBHOOK

### **Endpoint Principal**
```
POST https://media-upload-fix-3.preview.emergentagent.com/api/webhook
```

### **Format Multipart/Form-Data**
```bash
curl -X POST "https://media-upload-fix-3.preview.emergentagent.com/api/webhook" \
  -F "image=@/chemin/vers/image.jpg" \
  -F 'json_data={"title":"Mon Produit Gizmobbs","description":"Description du produit","url":"https://gizmobbs.com/produit","store":"gizmobbs"}'
```

### **Format JSON (Alternative)**
```bash
curl -X POST "https://media-upload-fix-3.preview.emergentagent.com/api/publishProduct" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mon Produit Gizmobbs",
    "description": "Description du produit",
    "image_url": "https://gizmobbs.com/image.jpg",
    "product_url": "https://gizmobbs.com/produit",
    "shop_type": "gizmobbs"
  }'
```

---

## 🎯 COMPORTEMENT SPÉCIFIQUE GIZMOBBS

### **Priorité Instagram :**
- ✅ **Toujours publier sur @logicamp_berger** quand `shop_type = "gizmobbs"`
- ✅ **Optimisation automatique** des images pour Instagram (1080x1080)
- ✅ **Caption adaptée** pour Instagram (hashtags, lien en bio)
- ✅ **Pas de publication Facebook** (Instagram uniquement)

### **Adaptations automatiques :**

**Original :**
```
Titre: "Smartphone XYZ"
Description: "Découvrez ce nouveau smartphone avec appareil photo pro"
URL: https://gizmobbs.com/smartphone-xyz
```

**Publication Instagram générée :**
```
Caption Instagram:
"Smartphone XYZ 📱

Découvrez ce nouveau smartphone avec appareil photo pro

🔗 Plus d'infos : lien en bio

#smartphone #tech #gizmobbs #innovation #mobile"
```

---

## 🔧 CONFIGURATION N8N

### **Node Webhook N8N pour Gizmobbs**

```json
{
  "method": "POST",
  "url": "https://media-upload-fix-3.preview.emergentagent.com/api/publishProduct",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "title": "{{ $json.product_name }}",
    "description": "📱 {{ $json.product_description }}\n\n🚀 Technologie de pointe chez Gizmobbs !",
    "image_url": "{{ $json.product_image }}",
    "product_url": "{{ $json.product_url }}",
    "shop_type": "gizmobbs"
  }
}
```

### **Workflow Automatique N8N**

```javascript
// Node: Détection Produit Gizmobbs
const product = $input.item.json;

// Force shop_type pour Instagram @logicamp_berger
if (product.brand === "gizmobbs" || 
    product.store_url.includes("gizmobbs.com") ||
    product.categories.includes("tech")) {
  
  return [{
    json: {
      title: product.name,
      description: `📱 ${product.description}\n\n✨ Innovation technologique chez Gizmobbs !`,
      image_url: product.featured_image,
      product_url: product.permalink,
      shop_type: "gizmobbs"  // → Publication automatique sur @logicamp_berger
    }
  }];
}
```

---

## 🧪 TESTS DISPONIBLES

### **Test Direct @logicamp_berger**
```bash
curl -X POST "https://media-upload-fix-3.preview.emergentagent.com/api/debug/test-logicamp-berger-webhook"
```

### **Test Configuration Gizmobbs**
```bash
curl -X POST "https://media-upload-fix-3.preview.emergentagent.com/api/debug/test-multi-platform-post?shop_type=gizmobbs"
```

### **Diagnostic Instagram Complet**
```bash
curl -X GET "https://media-upload-fix-3.preview.emergentagent.com/api/debug/instagram-complete-diagnosis"
```

---

## ⚠️ PRÉREQUIS AUTHENTIFICATION

### **Pour que ça fonctionne, vous devez :**

1. **Se connecter via l'interface web :**
   ```
   https://media-upload-fix-3.preview.emergentagent.com
   ```

2. **Utiliser le compte avec accès à :**
   ```
   🏢 Business Manager ID: 1715327795564432
   📱 Instagram: @logicamp_berger
   ```

3. **Vérifier les permissions :**
   - ✅ Instagram Business Account connecté
   - ✅ Permissions publication Instagram accordées
   - ✅ Page Facebook liée à @logicamp_berger

---

## 📊 RÉSULTATS ATTENDUS

### **Webhook avec shop_type: "gizmobbs" :**

```json
{
  "status": "success",
  "message": "Product 'Mon Produit' published successfully to Instagram @logicamp_berger",
  "instagram_post_id": "17841459952999804_123456789",
  "post_id": "uuid-post-id",
  "page_name": "Instagram @logicamp_berger",
  "page_id": "17841459952999804",
  "platform": "instagram",
  "shop_type": "gizmobbs",
  "business_manager_id": "1715327795564432",
  "platforms_published": {
    "instagram": true,
    "facebook": false
  }
}
```

---

## 🎉 AVANTAGES DE CETTE CONFIGURATION

### ✅ **Instagram Prioritaire pour Gizmobbs**
- Publication **UNIQUEMENT** sur @logicamp_berger
- Pas de dispersion sur Facebook
- Audience ciblée technologie/innovation

### ✅ **Optimisation Automatique**
- Images optimisées pour Instagram (ratio, taille, qualité)
- Caption adaptée avec hashtags pertinents
- Lien en bio standard Instagram

### ✅ **Monitoring Intégré**
- Logs détaillés de chaque publication
- Historique dans l'interface web
- Diagnostic complet disponible

---

## 🔧 RÉSOLUTION DE PROBLÈMES

### **Si publication échoue :**

1. **Vérifier l'authentification :**
   ```bash
   curl -X GET "https://media-upload-fix-3.preview.emergentagent.com/api/health"
   # Doit montrer users_count > 0
   ```

2. **Tester la configuration :**
   ```bash
   curl -X POST "https://media-upload-fix-3.preview.emergentagent.com/api/debug/test-logicamp-berger-webhook"
   ```

3. **Diagnostic complet :**
   ```bash
   curl -X GET "https://media-upload-fix-3.preview.emergentagent.com/api/debug/instagram-complete-diagnosis"
   ```

### **Messages d'erreur courants :**

- `"No authenticated user"` → Se connecter via l'interface web
- `"Business Manager 1715327795564432 non trouvé"` → Utiliser le bon compte
- `"@logicamp_berger non accessible"` → Vérifier connexion Instagram-Facebook

---

## 🎯 PROCHAINES ÉTAPES

1. **Connectez-vous** avec le compte ayant accès au Business Manager `1715327795564432`
2. **Testez** le webhook avec l'endpoint de test
3. **Lancez** vos workflows N8N avec `shop_type: "gizmobbs"`
4. **Vérifiez** les publications sur https://www.instagram.com/logicamp_berger/

**🚀 Votre webhook est maintenant optimisé pour @logicamp_berger !**