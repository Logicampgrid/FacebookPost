# Instagram Auto Publisher 📱

Script Python pour publier automatiquement des images et vidéos sur Instagram via l'API Graph de Meta.

## 🎯 Fonctionnalités

### ✅ Formats Supportés
- **Images**: `.jpg`, `.jpeg`, `.png`, `.webp`, `.heic`, `.avif`, `.bmp`, `.tiff`
- **Vidéos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`, `.m4v`

### 🔄 Conversions Automatiques
- **Images**: `.webp`, `.heic`, `.avif` → `.jpg` (format optimisé Instagram)
- **Vidéos**: Tous formats → `.mp4` (compatible Instagram Reels)
- **Redimensionnement**: Images automatiquement redimensionnées (max 1080px)
- **Durée**: Vidéos coupées à 60 secondes max

### 🛡️ Gestion des Erreurs
- **Fallback intelligent**: Upload direct → Multipart → Log erreur
- **Retry automatique**: 3 tentatives avec délais progressifs
- **Validation**: Vérification formats et tailles avant upload
- **Logs détaillés**: Traçabilité complète de chaque étape

### 📊 Limitations
- **Crédits Instagram**: Maximum 10 publications par jour
- **Rate limiting**: Pause automatique entre publications
- **Taille fichiers**: Optimisation automatique

## 🚀 Installation

### 1. Configuration automatique
```bash
python3 /app/setup_instagram_publisher.py
```

### 2. Installation manuelle des dépendances
```bash
pip install Pillow motor requests python-dotenv
apt-get install ffmpeg  # Pour conversion vidéo
```

### 3. Variables d'environnement
Vérifiez que ces variables sont configurées dans `/app/backend/.env`:
```bash
MONGO_URL=mongodb://localhost:27017
FACEBOOK_GRAPH_URL=https://graph.facebook.com/v18.0
```

## 📖 Utilisation

### Publication d'un fichier unique
```bash
python3 /app/instagram_auto_publisher.py \
    --file "photo.webp" \
    --caption "Belle photo de nos chiots! 🐕" \
    --hashtags "#bergerblancsuisse #chiots"
```

### Publication d'une vidéo
```bash
python3 /app/instagram_auto_publisher.py \
    --file "video.mov" \
    --caption "Nos chiots en plein jeu! 🎥" \
    --hashtags "#video #chiots #jeu"
```

### Publication par lots (dossier)
```bash
python3 /app/instagram_auto_publisher.py \
    --batch "/path/to/photos" \
    --caption "Collection de photos" \
    --hashtags "#collection #photos"
```

### Mode test (sans publication)
```bash
python3 /app/instagram_auto_publisher.py \
    --file "test.jpg" \
    --caption "Test" \
    --dry-run
```

## 🎛️ Options

| Option | Description | Exemple |
|--------|-------------|---------|
| `--file`, `-f` | Fichier unique à publier | `--file "image.webp"` |
| `--batch`, `-b` | Dossier de médias | `--batch "/photos"` |  
| `--caption`, `-c` | Description du post | `--caption "Belle photo!"` |
| `--hashtags`, `-t` | Hashtags | `--hashtags "#photo #art"` |
| `--dry-run` | Test sans publication | `--dry-run` |
| `--help` | Aide complète | `--help` |

## 📋 Exemples Complets

### Script d'exemple
Un script bash avec tous les exemples est disponible :
```bash
bash /app/example_instagram_usage.sh
```

### Intégration N8N/Webhook
```bash
# Publication depuis webhook
python3 /app/instagram_auto_publisher.py \
    --file "$WEBHOOK_IMAGE_PATH" \
    --caption "$WEBHOOK_TITLE" \
    --hashtags "#produit #nouveauté"
```

### Automatisation cron
```bash
# Publication quotidienne à 10h
0 10 * * * cd /app && python3 instagram_auto_publisher.py --batch "/media/daily"
```

## 🔍 Diagnostic

### Vérification configuration
```bash
python3 /app/setup_instagram_publisher.py
```

### Logs détaillés
```bash
tail -f /app/logs/instagram_publisher.log
```

### Test de connectivité
```bash
# Test sans publication
python3 /app/instagram_auto_publisher.py --file "test.jpg" --dry-run
```

## 📊 Rapport de Session

Après chaque exécution, un rapport détaillé s'affiche :

```
📊 RAPPORT DE SESSION INSTAGRAM
============================================
📁 Fichiers traités:     3
✅ Publications réussies: 2  
❌ Erreurs:              1
🔄 Conversions:          2
💳 Crédits utilisés:     2/10

📋 POSTS PUBLIÉS:
  • photo1.webp → ABC123 (image) 🔄
    🔗 https://instagram.com/p/ABC123
  • video1.mov → DEF456 (video) 🔄  
    🔗 https://instagram.com/p/DEF456
```

## 🔧 Configuration Avancée

### Personnalisation des formats
Modifiez les constantes dans le script :
```python
SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.heic'}
INSTAGRAM_MAX_IMAGE_SIZE = 1080  # pixels
INSTAGRAM_MAX_VIDEO_DURATION = 60  # secondes
```

### Compte Instagram spécifique  
Le script est configuré pour publier sur le compte Instagram de "Le Berger Blanc Suisse".
Pour changer : modifiez `BERGER_BLANC_SUISSE_PAGE_ID` dans le script.

## ⚠️ Limitations Importantes

1. **Authentification requise** : Un utilisateur doit être connecté via Facebook Business
2. **Permissions Meta** : Accès Instagram Business requis
3. **Rate limiting** : Respecte les limites d'API Instagram
4. **Formats propriétaires** : `.heic` nécessite des codecs spéciaux
5. **Connexion réseau** : Requiert une connexion stable pour uploads

## 🐛 Résolution de Problèmes

### Erreur "Aucun utilisateur authentifié"
```bash
# Vérifier la base de données
python3 -c "
import asyncio
import motor.motor_asyncio
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
print(asyncio.run(client.meta_posts.users.find_one()))
"
```

### Erreur "FFmpeg non trouvé"
```bash
apt-get update && apt-get install ffmpeg
```

### Erreur "Token expiré"
Re-authentifiez l'utilisateur via l'interface web de l'application.

### Problème de conversion HEIC
```bash
pip install pillow-heif
```

## 🔗 Intégration avec l'Application

Le script s'intègre parfaitement avec l'application existante :
- Utilise la même base de données MongoDB
- Respecte les tokens d'accès configurés  
- Compatible avec les logs et monitoring existants
- Peut être appelé depuis les webhooks N8N

## 📝 Notes Techniques

- **Threading**: Utilise `asyncio` pour les appels API asynchrones
- **Optimisation**: Conversion et redimensionnement automatiques
- **Sécurité**: Validation des formats et nettoyage des fichiers temporaires
- **Monitoring**: Logs structurés avec niveaux de détail
- **Performance**: Upload optimisé avec retry et timeouts

## 🆘 Support

En cas de problème :
1. Vérifiez les logs : `/app/logs/instagram_publisher.log`
2. Testez la configuration : `python3 /app/setup_instagram_publisher.py`
3. Mode debug : Ajoutez `--dry-run` pour tester sans publier
4. Vérifiez la connectivité : Testez l'API Graph directement

---

**🎉 Bon usage du script Instagram Auto Publisher !** 📱✨