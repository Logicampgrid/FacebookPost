# 🐕 Guide Gizmobbs Multi-Plateforme + Support Vidéo

## 🎉 Nouvelles Fonctionnalités Implémentées

### 1. 📘📸 Publication Multi-Plateforme pour Gizmobbs

Le store "gizmobbs" publie maintenant **simultanément** sur :
- **Facebook** : Page "Le Berger Blanc Suisse" 
- **Instagram** : Compte @logicamp_berger

### 2. 🎬 Support Vidéo Complet

Le système supporte maintenant les vidéos :
- **Formats supportés** : MP4, MOV, AVI, WebM, MKV
- **Taille maximum** : 100MB par fichier
- **Optimisation automatique** pour Facebook et Instagram

---

## 📋 Configuration Actuelle

### Store "gizmobbs" :
```json
{
  "name": "Le Berger Blanc Suisse",
  "expected_id": "102401876209415",
  "platform": "multi",
  "platforms": ["facebook", "instagram"],
  "instagram_username": "logicamp_berger"
}
```

### Store "gimobbs" (alias) :
Même configuration que "gizmobbs" pour compatibilité N8N.

---

## 🚀 Comment Utiliser

### 1. Via Webhook (N8N ou externe)

**Endpoint** : `POST /api/webhook`
**Content-Type** : `multipart/form-data`

#### Exemple cURL avec IMAGE :
```bash
curl -X POST "https://insta-post-fixer.preview.emergentagent.com/api/webhook" \
  -F "image=@mon_produit.jpg" \
  -F 'json_data={"title":"Nouveau produit Berger Blanc","description":"Découvrez notre nouvelle gamme","url":"https://gizmobbs.com/produit","store":"gizmobbs"}'
```

#### Exemple cURL avec VIDÉO :
```bash
curl -X POST "https://insta-post-fixer.preview.emergentagent.com/api/webhook" \
  -F "image=@demonstration.mp4" \
  -F 'json_data={"title":"Démonstration produit","description":"Vidéo de présentation","url":"https://gizmobbs.com/demo","store":"gizmobbs"}'
```

### 2. Via Interface Web

Dans l'interface web :
1. **Connectez-vous** avec Facebook
2. **Sélectionnez** le Business Manager approprié
3. **Choisissez** "Publication Intelligente" ou "Multi-plateforme"
4. **Ajoutez** votre image ou vidéo
5. **Publier** automatiquement sur les deux plateformes

---

## ✨ Fonctionnement Multi-Plateforme

### Quand vous publiez un produit gizmobbs :

#### 📘 **Publication Facebook** :
- Image/vidéo uploadée directement
- Description optimisée avec hashtags : `#bergerblancsuisse #chien #dog #animaux #gizmobbs`
- Lien produit ajouté en commentaire automatique
- **Image cliquable** qui redirige vers le produit

#### 📸 **Publication Instagram** :
- Image optimisée selon les spécifications Instagram (ratio, qualité)
- Vidéo optimisée (max 60MB pour Instagram)
- Description avec hashtags adaptés à Instagram
- Mention "Lien en bio" car Instagram ne permet pas les liens cliquables

### 🎬 **Support Vidéo Spécifique** :
- **Facebook** : Vidéos jusqu'à 100MB, formats multiples
- **Instagram** : Vidéos optimisées max 60MB, ratio ajusté automatiquement
- **Détection automatique** du type de média (image vs vidéo)

---

## 🧪 Tests et Validation

### Tester la Configuration :
```bash
# Test de la configuration multi-plateforme
curl "http://localhost:8001/api/debug/store-platforms/gizmobbs"

# Test du webhook
curl "http://localhost:8001/api/webhook"
```

### Résultat Attendu :
```json
{
  "shop_type": "gizmobbs",
  "platforms": {
    "main_page": {
      "id": "102401876209415",
      "name": "Le Berger Blanc Suisse"
    },
    "instagram_accounts": [
      {
        "id": "...",
        "username": "logicamp_berger"
      }
    ]
  }
}
```

---

## 📊 Avantages

### ✅ **Publication Efficace** :
- **1 action = 2 publications** (Facebook + Instagram)
- Gain de temps considérable
- Cohérence du message sur les deux plateformes

### ✅ **Optimisation Automatique** :
- Images adaptées à chaque plateforme
- Vidéos optimisées selon les contraintes
- Hashtags spécifiques à chaque réseau

### ✅ **Flexibilité** :
- Support images ET vidéos
- Webhook compatible N8N
- Interface web intuitive

---

## 🔧 Maintenance

### Logs à Surveiller :
```bash
# Logs backend
tail -f /var/log/supervisor/backend.err.log

# Rechercher publications gizmobbs
grep "gizmobbs" /var/log/supervisor/backend.err.log
```

### Redémarrage si Nécessaire :
```bash
sudo supervisorctl restart backend
```

---

## 📈 Prochaines Améliorations Possibles

1. **Analytics** : Suivi des performances par plateforme
2. **Programmation** : Publication différée sur les deux plateformes
3. **Templates** : Messages pré-configurés pour gizmobbs
4. **Compression vidéo** : Optimisation avancée avec ffmpeg

---

## 🎯 Résumé

**Avant** : gizmobbs → Instagram seulement
**Maintenant** : gizmobbs → **Facebook + Instagram simultanément**
**Bonus** : Support complet des vidéos sur les deux plateformes !

🎉 **La publication multi-plateforme est maintenant opérationnelle !**