# SOLUTION : Résolution de l'erreur "Invalid image type: video/mp4"

## Problème Initial
L'erreur `Bad request - please check your parameters Invalid image type: video/mp4. Allowed: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']` se produisait car le système traitait les vidéos comme des images et tentait de les envoyer vers l'endpoint `/photos` au lieu de `/videos`.

## Solution Implémentée

### 🚀 Nouvelle Fonction AUTO-ROUTING
Ajout d'une fonction `auto_route_media_to_facebook_instagram()` qui :

1. **Détecte automatiquement le type de fichier** (image vs vidéo) via `detect_media_type_from_content()`
2. **Route automatiquement** vers le bon endpoint Facebook :
   - Images → `/photos`
   - Vidéos → `/videos`
3. **Utilise le champ "store"** pour publier sur la bonne page selon `SHOP_PAGE_MAPPING`
4. **Publie sur Facebook ET Instagram** pour les deux types de médias
5. **Respecte la limite de 10 crédits** Emergent par publication

### 📋 Détection Automatique de Type
La fonction `detect_media_type_from_content()` utilise :
- **Extension de fichier** (mp4, mov, avi, webm → vidéo)
- **Magic bytes** (signatures de fichiers) pour détecter le type réel
- **Fallback intelligent** vers image si incertain

### 🔄 Modification du Webhook Principal
Le webhook `/api/webhook` a été modifié pour :
- Accepter les champs `image` ET `video` dans les requêtes multipart
- Détecter automatiquement le type de média uploadé
- Router vers la nouvelle fonction AUTO-ROUTING en priorité
- Conserver les fallbacks existants pour compatibilité

## Fonctionnalités Ajoutées

### ✅ Gestion Automatique des Types de Fichiers
- **Images supportées** : JPEG, PNG, WebP, GIF
- **Vidéos supportées** : MP4, MOV, AVI, WebM, MKV
- **Détection automatique** sans configuration manuelle

### ✅ Routage Intelligent par Store
Utilise le champ `"store"` pour router vers la bonne page :
```json
{
  "store": "gizmobbs",     // → Page "Le Berger Blanc Suisse"
  "store": "outdoor",      // → Page "Le Berger Blanc Suisse" 
  "store": "logicantiq"    // → Page "Le Berger Blanc Suisse"
}
```

### ✅ Publication Multi-Plateformes
- **Facebook** : Via `/photos` (images) ou `/videos` (vidéos)
- **Instagram** : Gestion automatique des containers media pour les deux types
- **Liens cliquables** : Chaque publication redirige vers l'URL produit

### ✅ Gestion des Crédits Emergent
- **1 crédit** : Upload du média vers Facebook
- **1 crédit** : Publication sur Facebook
- **1 crédit** : Publication sur Instagram (si configuré)
- **Maximum 10 crédits** par requête webhook

## Tests de Validation

### Test 1 : Vidéo MP4
```bash
# Avant : Invalid image type: video/mp4
# Après : ✅ SUCCESS: Vidéo MP4 acceptée!
curl -X POST webhook -F "video=@test.mp4" -F 'json_data={"store":"gizmobbs"...}'
```

### Test 2 : Images Multiple Formats
```bash
# JPEG, PNG, WebP, GIF tous supportés
curl -X POST webhook -F "image=@test.jpg" -F 'json_data={"store":"outdoor"...}'
```

### Test 3 : Détection Automatique
```bash
# Le système détecte automatiquement image vs vidéo
curl -X POST /api/test/auto-routing-media
```

## Endpoint de Test Ajouté
`POST /api/test/auto-routing-media` - Test la détection automatique et le routage

## Résultat Final

### ❌ Avant (Erreur)
```
HTTP 400: Invalid image type: video/mp4. Allowed: ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
```

### ✅ Après (Succès)
```json
{
  "success": true,
  "message": "✅ Média publié avec succès via AUTO-ROUTING!",
  "platforms_used": ["facebook", "instagram"],
  "credits_used": 3,
  "media_type": "video",
  "store": "gizmobbs"
}
```

## Compatibilité
- ✅ **Rétrocompatible** avec les requêtes existantes
- ✅ **Fallbacks conservés** si la nouvelle stratégie échoue
- ✅ **Aucun changement** requis côté N8N
- ✅ **Respecte les crédits** Emergent existants

## Impact
1. **Plus d'erreur "Invalid image type: video/mp4"** 
2. **Support complet des vidéos** sur Facebook et Instagram
3. **Routage automatique** selon le type de média
4. **Publication intelligente** selon le champ "store"
5. **Limite de 10 crédits** respectée par publication