# Guide d'Utilisation - Validation et Conversion d'Images

## 🎯 Objectif

Implémentation de la validation et conversion automatique d'images pour Instagram/Facebook selon les spécifications :
- Vérification que Content-Type est bien image
- Conversion forcée vers JPEG avant upload  
- Support des formats WebP/HEIC avec pillow-heif et pillow-webp
- Assurance que le fichier final fait ≥1 Ko
- Upload via FTP pour obtenir URL HTTPS stable
- Publication sur Instagram avec URL FTP HTTPS finale

## 🔧 Fonctions Implémentées

### 1. `validate_and_prepare_image(file_path, max_retries=2)`

**Fonction principale de validation et conversion**

```python
def validate_and_prepare_image(file_path: str, max_retries: int = 2) -> str:
    """
    Valide et prépare une image pour Instagram/Facebook.
    - Vérifie la taille minimale (1 Ko)
    - Détecte le format via magic bytes
    - Convertit WebP/HEIC → JPEG
    - Retourne le chemin du fichier final prêt à uploader
    """
```

**Paramètres :**
- `file_path` : Chemin vers le fichier image à traiter
- `max_retries` : Nombre de tentatives en cas d'échec (défaut: 2)

**Retourne :** Chemin du fichier JPEG final prêt pour upload

**Formats supportés :**
- ✅ JPEG → JPEG (optimisé)
- ✅ PNG → JPEG  
- ✅ WebP → JPEG
- ✅ HEIC/HEIF → JPEG

### 2. `upload_to_ftp(file_path)`

**Upload FTP pour URL HTTPS stable**

```python
def upload_to_ftp(file_path: str) -> str:
    """
    Upload un fichier vers serveur FTP et retourne URL HTTPS stable
    Configuration FTP depuis les variables d'environnement
    """
```

**Configuration requise dans `.env` :**
```bash
FTP_HOST=your-ftp-server.com
FTP_PORT=21
FTP_USER=your-ftp-username  
FTP_PASSWORD=your-ftp-password
FTP_DIRECTORY=/uploads/
FTP_BASE_URL=https://your-domain.com/uploads/
```

### 3. `poster_media_enhanced(file_path, product_link)`

**Fonction complète de publication**

```python
def poster_media_enhanced(file_path: str, product_link: str):
    """
    Poster un média sur Instagram et Facebook avec validation et conversion
    1️⃣ Préparer l'image - validate_and_prepare_image()
    2️⃣ Upload FTP - obtenir URL HTTPS stable  
    3️⃣ Publier sur Instagram
    4️⃣ Publier sur Facebook
    """
```

## 🚀 Utilisation

### Test Simple via API

**Endpoint de test disponible :**
```
POST /api/test-image-validation
```

**Exemple avec curl :**
```bash
curl -X POST \
  http://localhost:8001/api/test-image-validation \
  -F "file=@mon_image.webp"
```

**Réponse :**
```json
{
  "success": true,
  "message": "Image validée et convertie avec succès",
  "prepared_file": "C:\\gizmobbs\\uploads/image_converted.jpg",
  "final_size_mb": 0.85,
  "original_filename": "mon_image.webp"
}
```

### Utilisation Programmatique

```python
# Import des fonctions
from server import validate_and_prepare_image, poster_media_enhanced

# 1. Validation et conversion simple
try:
    prepared_file = validate_and_prepare_image("/path/to/image.webp")
    print(f"Image prête: {prepared_file}")
except Exception as e:
    print(f"Erreur: {e}")

# 2. Publication complète (nécessite configuration FTP + API tokens)
result = poster_media_enhanced("/path/to/image.webp", "https://monsite.com/produit")
if result["success"]:
    print("Publication réussie!")
else:
    print(f"Erreur: {result['error']}")
```

## ⚙️ Configuration Complète

### 1. Variables d'Environnement FTP

Copier `.env.example` vers `.env` et remplir :

```bash
# Configuration FTP
FTP_HOST=votre-serveur-ftp.com
FTP_PORT=21
FTP_USER=votre-utilisateur-ftp
FTP_PASSWORD=votre-mot-de-passe-ftp
FTP_DIRECTORY=/uploads/
FTP_BASE_URL=https://votre-domaine.com/uploads/

# Configuration Instagram API
INSTAGRAM_USER_ID=votre-instagram-user-id
INSTAGRAM_ACCESS_TOKEN=votre-instagram-access-token

# Configuration Facebook API
FACEBOOK_PAGE_ID=votre-facebook-page-id  
FACEBOOK_ACCESS_TOKEN=votre-facebook-access-token
```

### 2. Installation des Dépendances

```bash
cd /app/backend
pip install pillow-heif pillow[webp]
```

### 3. Redémarrage du Service

```bash
sudo supervisorctl restart backend
```

## 🧪 Tests

### Test des Fonctions Principales

```bash
cd /app
python test_image_validation.py
python test_real_image.py
```

### Test via API

```bash
# Créer une image de test
curl -X POST \
  http://localhost:8001/api/test-image-validation \
  -F "file=@/path/to/test/image.jpg"
```

## 📋 Points Importants

### ✅ Avantages de l'Implémentation

1. **Validation robuste** : Vérification taille minimale (1 Ko)
2. **Conversion automatique** : WebP/HEIC → JPEG sans intervention
3. **Qualité optimisée** : JPEG qualité 95 pour Instagram/Facebook
4. **URL stable** : Upload FTP évite les problèmes d'URLs temporaires (ngrok)
5. **Retry logic** : Tentatives multiples en cas d'échec
6. **Logging détaillé** : Traçabilité complète des opérations

### ⚠️ Limitations et Prérequis

1. **Configuration FTP requise** : Serveur FTP accessible nécessaire
2. **Tokens API requis** : Instagram/Facebook access tokens
3. **Formats supportés** : JPEG, PNG, WebP, HEIC/HEIF
4. **Taille minimum** : 1 Ko minimum après conversion
5. **Dépendances** : pillow-heif pour HEIC, pillow[webp] pour WebP

## 🔍 Debugging

### Logs à Surveiller

```
✅ Image préparée: /path/to/result.jpg
✅ Upload FTP réussi: https://domain.com/uploads/file.jpg
✅ Publication Instagram réussie: 123456789
✅ Publication Facebook réussie: 987654321
```

### Erreurs Communes

1. **"Fichier trop petit"** → Image < 1 Ko, augmenter qualité/résolution
2. **"Erreur upload FTP"** → Vérifier credentials FTP dans .env
3. **"Publication échouée"** → Vérifier tokens Instagram/Facebook
4. **"Format non supporté"** → Vérifier pillow-heif installé pour HEIC

## 🎯 Intégration dans le Flux Existant

Les nouvelles fonctions sont **indépendantes** et n'interfèrent pas avec `poster_media()` existant.

**Options d'intégration :**

1. **Remplacement progressif** : Utiliser `poster_media_enhanced()` pour nouveaux uploads
2. **API parallèle** : Utiliser `/api/test-image-validation` pour validation avant upload
3. **Module standalone** : Importer et utiliser `validate_and_prepare_image()` selon besoins

## 📈 Prochaines Étapes

1. **Configurer FTP** : Remplir variables .env avec serveur FTP réel
2. **Configurer API tokens** : Instagram/Facebook access tokens  
3. **Tests en production** : Tester avec vraies images et publications
4. **Monitoring** : Surveiller logs et performance
5. **Optimisations** : Ajuster qualité JPEG selon retours utilisateur