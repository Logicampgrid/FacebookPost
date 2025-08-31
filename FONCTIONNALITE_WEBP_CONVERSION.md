# Fonctionnalité de Conversion Automatique WebP → JPEG

## Objectif
Détecter automatiquement les médias au format .webp et les convertir en .jpeg avant upload sur Facebook ou Instagram, en conservant la résolution et la qualité maximale.

## Fichier modifié
- ✅ **server.py uniquement** (comme demandé)

## Fonction principale ajoutée

### `convert_webp_to_jpeg(input_path: str)`
**Localisation:** Ligne ~378 (avant `convert_media_for_social_platforms`)

**Fonctionnalités:**
- ✅ Détection automatique du format WebP
- ✅ Conversion avec qualité JPEG 95% (maximale)
- ✅ Conservation de la résolution originale
- ✅ Gestion de la transparence (fond blanc automatique)
- ✅ Logs détaillés avec print()
- ✅ Validation du format d'entrée

## Points d'intégration

### 1. `download_media_reliably()` - URLs externes
**Localisation:** Lignes ~276-292 et ~359-375

**Logique ajoutée:**
```python
# CONVERSION AUTOMATIQUE WebP → JPEG
if media_type == 'image' and extension and extension.lower() == '.webp':
    print(f"[WebP DÉTECTÉ] Conversion automatique en JPEG requise")
    success, jpeg_path, error_msg = await convert_webp_to_jpeg(local_path)
    if success:
        os.unlink(local_path)  # Supprimer WebP original
        local_path = jpeg_path  # Utiliser JPEG converti
        print(f"[WebP CONVERTI] Fichier final → {local_path}")
```

**S'applique à:**
- ✅ URLs externes téléchargées
- ✅ Fallback binaire

### 2. `post_to_instagram()` - Fichiers locaux
**Localisation:** Lignes ~7203-7220

**Logique ajoutée:**
```python
# CONVERSION AUTOMATIQUE WebP → JPEG pour fichiers locaux
if media_type == "image" and local_file_path.lower().endswith('.webp'):
    print(f"[WebP DÉTECTÉ] Fichier local WebP → conversion JPEG requise")
    success, jpeg_path, error_msg = await convert_webp_to_jpeg(local_file_path)
    if success:
        upload_file_path = jpeg_path
        print(f"[WebP CONVERTI] Fichier Instagram → {upload_file_path}")
```

### 3. `post_to_facebook()` - Fichiers locaux
**Localisation:** Lignes ~6770-6787

**Logique ajoutée:**
```python
# CONVERSION AUTOMATIQUE WebP → JPEG pour fichiers locaux Facebook
if local_file_path.lower().endswith('.webp'):
    print(f"[WebP DÉTECTÉ] Fichier local WebP → conversion JPEG requise (Facebook)")
    success, jpeg_path, error_msg = await convert_webp_to_jpeg(local_file_path)
    if success:
        upload_file_path = jpeg_path
        print(f"[WebP CONVERTI] Fichier Facebook → {upload_file_path}")
```

## Flux de traitement

### Scenario 1: URL WebP externe
1. `download_media_reliably()` télécharge le fichier WebP
2. Détection automatique de l'extension `.webp`
3. Conversion → fichier JPEG avec `_converted.jpeg`
4. Suppression du WebP original
5. Retour du chemin JPEG pour upload

### Scenario 2: Fichier WebP local
1. `post_to_instagram()` ou `post_to_facebook()` détecte `.webp`
2. Conversion → fichier JPEG avec `_converted.jpeg`
3. Upload du fichier JPEG converti
4. WebP original préservé (pas supprimé pour fichiers locaux)

## Logs ajoutés

### Détection
```
[WebP DÉTECTÉ] Conversion automatique en JPEG requise
[WebP DÉTECTÉ] Fichier local WebP → conversion JPEG requise
[WebP DÉTECTÉ] Fichier local WebP → conversion JPEG requise (Facebook)
```

### Conversion
```
[CONVERSION WebP] Fichier détecté → /path/to/file.webp
[CONVERSION WebP] Résolution originale → 1920x1080
[CONVERSION WebP] Mode couleur → RGB
[CONVERSION WebP] Conversion réussie → /path/to/file_converted.jpeg
[CONVERSION WebP] Qualité JPEG → 95% (maximale)
```

### Résultat
```
[WebP CONVERTI] Fichier final → /path/to/converted.jpeg
[WebP CONVERTI] Fichier Instagram → /path/to/converted.jpeg
[WebP CONVERTI] Fichier Facebook → /path/to/converted.jpeg
```

### Erreurs
```
[WebP ERREUR] Conversion échouée: [message d'erreur]
```

## Caractéristiques techniques

### Librairie utilisée
- ✅ **Pillow (PIL)** - Déjà importé dans server.py

### Paramètres de conversion
- ✅ **Qualité JPEG:** 95% (maximale compatible)
- ✅ **Optimisation:** Activée (`optimize=True`)
- ✅ **Résolution:** Conservée à l'identique
- ✅ **Transparence:** Fond blanc automatique pour JPEG

### Gestion des erreurs
- ✅ Validation du format WebP avant conversion
- ✅ Fallback vers fichier original si conversion échoue
- ✅ Logs d'erreur détaillés
- ✅ Nettoyage automatique en cas d'échec

## Compatibilité

### Formats d'entrée supportés
- ✅ **WebP avec transparence** → JPEG avec fond blanc
- ✅ **WebP sans transparence** → JPEG direct
- ✅ **WebP animé** → Premier frame en JPEG

### Flux préservés
- ✅ **Images autres formats** → Aucun changement
- ✅ **Vidéos** → Aucun changement
- ✅ **Logique Facebook/Instagram** → Aucun changement
- ✅ **Webhook n8n** → Aucun changement

## Validation
- ✅ Test fonctionnel complet
- ✅ Serveur redémarré sans erreur
- ✅ Conversion WebP → JPEG validée
- ✅ Conservation résolution validée
- ✅ Détection format non-WebP validée
- ✅ Intégration transparente confirmée

## Status : ✅ FONCTIONNEL
La conversion automatique WebP → JPEG est opérationnelle sur tous les flux d'upload Facebook et Instagram.