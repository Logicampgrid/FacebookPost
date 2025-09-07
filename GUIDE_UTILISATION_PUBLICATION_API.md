# 📢 Guide d'utilisation - API Publication Facebook/Instagram

## 🚀 Vue d'ensemble

Cette API permet de publier automatiquement du contenu sur Facebook et Instagram pour 4 boutiques différentes :
- **logicantiq** - Antiquités
- **logicampoutdoor** - Matériel de camping
- **bergerblancsuisse** - Élevage de chiens
- **gizmobbs** - Gadgets technologiques

## 🛠️ Configuration

### Variables d'environnement (.env)

```bash
# Mode test (true = simulation, false = vraies publications)
PUBLICATION_TEST_MODE=true

# Tokens d'accès Facebook pour chaque boutique
FB_ACCESS_TOKEN_LOGICANTIQ=<YOUR_TOKEN>
FB_ACCESS_TOKEN_LOGICAMPOUTDOOR=<YOUR_TOKEN>
FB_ACCESS_TOKEN_BERGER=<YOUR_TOKEN>
FB_ACCESS_TOKEN_GIZMO=<YOUR_TOKEN>

# IDs des pages Facebook
FB_PAGE_ID_LOGICANTIQ=<YOUR_PAGE_ID>
FB_PAGE_ID_LOGICAMPOUTDOOR=<YOUR_PAGE_ID>
FB_PAGE_ID_BERGER=<YOUR_PAGE_ID>
FB_PAGE_ID_GIZMO=<YOUR_PAGE_ID>

# IDs des comptes Instagram
IG_USER_ID_LOGICANTIQ=<YOUR_IG_ID>
IG_USER_ID_LOGICAMPOUTDOOR=<YOUR_IG_ID>
IG_USER_ID_BERGER=<YOUR_IG_ID>
IG_USER_ID_GIZMO=<YOUR_IG_ID>
```

## 📡 Endpoints API

### 1. **Health Check**
```bash
GET /api/health
```
Vérifie l'état du système et la configuration des boutiques.

**Exemple de réponse :**
```json
{
  "status": "healthy",
  "publication": {
    "test_mode": true,
    "stores_configured": 4,
    "total_stores": 4
  },
  "stores": {
    "logicantiq": {
      "fb_page_id": true,
      "ig_user_id": true,
      "access_token": true
    }
  }
}
```

### 2. **Liste des boutiques**
```bash
GET /api/stores
```
Obtient la liste des boutiques configurées.

### 3. **Publication principale**
```bash
POST /api/publish
```

**Corps de la requête :**
```json
{
  "store": "logicantiq",
  "message": "Découvrez ce magnifique vase ancien ! 🏺",
  "product_url": "https://logicantiq.com/produit/vase-ancien",
  "image_url": "https://logicantiq.com/images/vase.jpg",
  "platforms": ["facebook", "instagram"]
}
```

**Paramètres :**
- `store` (requis) : Une des 4 boutiques
- `message` (requis) : Texte du post
- `product_url` (requis) : URL du produit
- `image_url` (optionnel) : URL de l'image (extrait automatiquement si non fournie)
- `platforms` (optionnel) : `["facebook"]`, `["instagram"]` ou `["facebook", "instagram"]` (défaut)

### 4. **Historique des publications**
```bash
GET /api/publications?store=logicantiq&limit=10
```

### 5. **Test de configuration**
```bash
POST /api/test-config?store=logicantiq
```
Teste la validité des tokens sans publier.

## 🔧 Utilisation pratique

### Exemple 1 : Publication complète avec image
```bash
curl -X POST "http://localhost:8001/api/publish" \
-H "Content-Type: application/json" \
-d '{
  "store": "logicantiq",
  "message": "🏺 Vase Ming authentique du 15ème siècle",
  "product_url": "https://logicantiq.com/produit/vase-ming-15eme",
  "image_url": "https://logicantiq.com/images/vase-ming.jpg"
}'
```

### Exemple 2 : Publication Facebook seulement
```bash
curl -X POST "http://localhost:8001/api/publish" \
-H "Content-Type: application/json" \
-d '{
  "store": "logicampoutdoor",
  "message": "🏕️ Nouvelle tente 4 saisons ultra-légère !",
  "product_url": "https://logicampoutdoor.com/tente-ultralight",
  "platforms": ["facebook"]
}'
```

### Exemple 3 : Instagram avec extraction d'image automatique
```bash
curl -X POST "http://localhost:8001/api/publish" \
-H "Content-Type: application/json" \
-d '{
  "store": "bergerblancsuisse",
  "message": "🐕 Magnifique portée de chiots disponibles !",
  "product_url": "https://bergerblancsuisse.com/portee-2024",
  "platforms": ["instagram"]
}'
```

## 🎯 Spécificités par plateforme

### Facebook
- **API utilisée** : Facebook Graph API v18.0
- **Endpoint** : `POST /{page_id}/feed`
- **Paramètres** : `message`, `link`, `access_token`
- **Pas d'image requise** : Facebook génère automatiquement l'aperçu du lien

### Instagram
- **API utilisée** : Instagram Graph API
- **Processus en 2 étapes** :
  1. Création du conteneur : `POST /{ig_user_id}/media`
  2. Publication : `POST /{ig_user_id}/media_publish`
- **Image obligatoire** : Instagram nécessite toujours une image
- **Légende** : Message + URL du produit

## 🧪 Mode Test vs Production

### Mode Test (PUBLICATION_TEST_MODE=true)
- **Aucune vraie publication** sur les réseaux sociaux
- Simule les réponses des API
- Permet de tester la logique sans impact
- IDs de test générés automatiquement

### Mode Production (PUBLICATION_TEST_MODE=false)
- **Vraies publications** sur Facebook et Instagram
- Utilise les vraies API Meta
- Nécessite des tokens valides
- Attention aux limites de taux d'API

## 🚨 Gestion d'erreurs

### Erreurs courantes

| Code | Erreur | Solution |
|------|--------|----------|
| 400 | Store inconnu | Vérifier le nom du store |
| 400 | Message vide | Fournir un message non vide |
| 400 | URL produit manquante | Fournir une URL valide |
| 500 | Configuration manquante | Vérifier les tokens dans .env |
| 500 | Token invalide | Renouveler le token Facebook |

### Exemple de réponse d'erreur
```json
{
  "success": false,
  "store": "logicantiq",
  "platforms": ["facebook", "instagram"],
  "facebook_result": {
    "id": "fb_post_12345",
    "message": "Post publié"
  },
  "instagram_result": null,
  "errors": [
    "Impossible d'extraire une image pour Instagram",
    "Échec Instagram: Image requise"
  ]
}
```

## 🔄 Workflow recommandé

1. **Test de configuration**
   ```bash
   curl -X POST "http://localhost:8001/api/test-config?store=logicantiq"
   ```

2. **Publication en mode test**
   ```bash
   # Avec PUBLICATION_TEST_MODE=true
   curl -X POST "http://localhost:8001/api/publish" -d '{...}'
   ```

3. **Vérification de l'historique**
   ```bash
   curl "http://localhost:8001/api/publications"
   ```

4. **Passage en production**
   ```bash
   # Modifier .env : PUBLICATION_TEST_MODE=false
   sudo supervisorctl restart backend
   ```

## 🔍 Extraction automatique d'images

L'API peut extraire automatiquement l'image d'une page web via :
1. **Meta tag Open Graph** : `<meta property="og:image" content="...">`
2. **Première image trouvée** : Premier tag `<img>` de la page
3. **URLs relatives** : Converties automatiquement en URLs absolues

## 📝 Logs et debugging

Les logs sont disponibles via :
```bash
tail -f /var/log/supervisor/backend.out.log
```

Format des logs :
```
📢 [14:30:15] [PUBLISH] Publication Facebook pour logicantiq
✅ [14:30:16] [PUBLISH] Publication Facebook réussie: 12345
🧪 [14:30:16] [PUBLISH] MODE TEST - Publication Instagram simulée
```

## 💡 Conseils d'utilisation

1. **Toujours tester d'abord** en mode test
2. **Vérifier les tokens** régulièrement (ils expirent)
3. **Prévoir les images** pour Instagram
4. **Surveiller les limites** de taux d'API Facebook
5. **Utiliser des URLs publiques** pour les images
6. **Messages adaptés** aux contraintes de chaque plateforme

## 🔧 Maintenance

### Renouvellement des tokens
1. Générer de nouveaux tokens via Facebook Business Manager
2. Mettre à jour le fichier `.env`
3. Redémarrer le backend : `sudo supervisorctl restart backend`

### Ajout d'une nouvelle boutique
1. Ajouter la configuration dans `STORES` (server.py)
2. Ajouter les nouvelles variables d'environnement
3. Redémarrer le backend

---

**🎉 Votre API de publication multi-plateforme est prête !**