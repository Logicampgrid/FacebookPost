# 🚀 TUNNEL INSTAGRAM GRATUIT - Guide d'utilisation

## 📋 Vue d'ensemble

Votre plateforme dispose d'un **tunnel Instagram gratuit** permettant de publier automatiquement sur Instagram (@logicamp_berger) via plusieurs méthodes.

## 🔑 Configuration initiale (Une seule fois)

### Étape 1 : Authentification
1. Allez sur http://localhost:3000
2. Cliquez sur "Se connecter avec Facebook"
3. Connectez-vous avec le compte ayant accès au Business Manager contenant @logicamp_berger

### Étape 2 : Vérification
Exécutez le test de vérification :
```bash
cd /app
python3 test_instagram_tunnel.py
```

## 🌐 Utilisation du tunnel via Webhook (Recommandé)

### URL du tunnel
```
https://code-craftsman-57.preview.emergentagent.com/api/webhook
```

### Méthode d'utilisation

#### Avec cURL :
```bash
curl -X POST "https://code-craftsman-57.preview.emergentagent.com/api/webhook" \
  -F "image=@/path/to/your/image.jpg" \
  -F 'json_data={"title":"Titre du post","description":"Description du produit","url":"https://votresite.com/produit","store":"gizmobbs"}'
```

#### Paramètres requis :

**Champ `image`** (fichier) :
- Formats supportés : JPG, PNG, GIF, WebP, MP4, MOV, AVI, WebM
- Optimisation automatique pour Instagram
- Correction d'orientation EXIF

**Champ `json_data`** (JSON string) :
```json
{
  "title": "Titre du post (requis)",
  "description": "Description du post (requis)",
  "url": "URL du produit/lien (requis)",
  "store": "Magasin cible (optionnel)"
}
```

#### Magasins disponibles :
- `outdoor` → @logicamp_berger
- `gizmobbs` → @logicamp_berger  
- `gimobbs` → @logicamp_berger
- `logicantiq` → @logicamp_berger
- `ma-boutique` → @logicamp_berger

## 🖥️ Utilisation via interface web

1. Allez sur http://localhost:3000
2. Onglet "Créer un Post"
3. Sélectionnez la plateforme Instagram
4. Ajoutez votre contenu et images
5. Cliquez "Publier"

## 📱 Fonctionnalités Instagram automatiques

### Optimisation des médias
- ✅ Redimensionnement automatique (1440px max)
- ✅ Respect des ratios Instagram (4:5 à 1.91:1)
- ✅ Correction d'orientation EXIF
- ✅ Compression optimisée (< 8MB)
- ✅ Support vidéo (< 60MB)

### Amélioration des captions
- ✅ Ajout automatique de hashtags pertinents
- ✅ "Lien en bio" pour les URLs
- ✅ Hashtags par magasin :
  - outdoor/logicamp → `#bergerblancsuisse #chien #dog #outdoor #logicampoutdoor`
  - gizmobbs → `#bergerblancsuisse #chien #dog #animaux #gizmobbs`

### Publication en 2 étapes
1. **Création du container média** (upload + validation)
2. **Publication du container** (post visible sur Instagram)

## 🧪 Tests et diagnostics

### Test complet du tunnel
```bash
cd /app
python3 test_instagram_tunnel.py
```

### Diagnostic Instagram détaillé
```bash
curl -s "http://localhost:8001/api/debug/instagram-complete-diagnosis" | python3 -m json.tool
```

### Test de publication pour un magasin
```bash
curl -X POST "http://localhost:8001/api/debug/test-instagram-webhook-universal?shop_type=gizmobbs"
```

## 🔧 Résolution de problèmes

### Problème : "No authenticated user"
**Solution :** Connectez-vous via http://localhost:3000

### Problème : "No Instagram Business account found"
**Solution :** Vérifiez que @logicamp_berger est connecté à une page Facebook dans votre Business Manager

### Problème : "Instagram API Error 9004"
**Solution :** Le système utilise automatiquement l'upload multipart pour éviter ce problème

### Problème : "Permissions error"
**Solution :** Vérifiez les permissions Instagram Business dans Facebook Developer Console

## 📊 Statut actuel

### ✅ Fonctionnel
- Backend API complet
- Endpoint webhook public
- Configuration multi-magasins
- Optimisation automatique des médias
- Interface web complète

### 🔑 Requis pour activation
- Authentification Facebook Business Manager (une seule fois)
- Accès au compte @logicamp_berger

## 🎯 Utilisation recommandée

**Pour publications automatiques :** Utilisez l'endpoint webhook
**Pour publications manuelles :** Utilisez l'interface web
**Pour tests :** Utilisez les scripts de diagnostic

## 📞 Support

En cas de problème, consultez les logs :
```bash
# Backend
tail -f /var/log/supervisor/backend.err.log

# Tests
cd /app && python3 instagram_tunnel_fix.py
```

---

🎉 **Votre tunnel Instagram gratuit est prêt à l'emploi !**

Une fois connecté avec Facebook Business Manager, vous pourrez publier automatiquement sur Instagram via l'API webhook ou l'interface web.