# Modifications pour la prise en charge des vidéos Instagram

## Objectif
Ajouter la prise en charge des vidéos pour les publications Instagram tout en conservant le comportement existant pour les images.

## Fichier modifié
- `server.py` uniquement (comme demandé)

## Modifications apportées

### 1. Fonction `wait_for_video_container_ready` (ligne 1567)
**Modifications :**
- ✅ Intervalle de polling : **10s → 3s** (comme spécifié)
- ✅ Timeout max : **60s** (respecté)
- ✅ Fields API optimisé : `status_code` seulement
- ✅ Log amélioré : "Container vidéo prêt → publication..."
- ✅ Log timeout plus explicite

### 2. Fonction `post_to_instagram` (ligne 7017)
**Modifications des logs :**
- ✅ **Ligne 7052** : `"[Instagram] Vidéo détectée → création container..."`
- ✅ **Ligne 7191** : `"[Instagram] Container vidéo prêt → publication..."`
- ✅ **Ligne 7290** : `"[Instagram] Upload vidéo réussi"`

## Workflow vidéo Instagram (inchangé dans la logique)

### Étape 1 : Détection du média
```
Si le média est une vidéo (extension .mp4, .mov, etc.) :
→ Log: "[Instagram] Vidéo détectée → création container..."
```

### Étape 2 : Création du container
```
POST /{ig_user_id}/media avec :
- media_type=VIDEO
- Fichier vidéo en multipart upload
```

### Étape 3 : Polling du statut
```
GET /{container_id}?fields=status_code toutes les 3s (max 60s)
- Si status_code = FINISHED → Étape 4
- Si status_code = ERROR/EXPIRED → Abandon
- Si timeout → Log erreur et abandon
```

### Étape 4 : Publication
```
POST /{ig_user_id}/media_publish avec container_id
→ Log: "[Instagram] Upload vidéo réussi"
```

## Logs ajoutés pour le débogage

1. **Détection vidéo** : `"[Instagram] Vidéo détectée → création container..."`
2. **Container prêt** : `"[Instagram] Container vidéo prêt → publication..."`
3. **Upload réussi** : `"[Instagram] Upload vidéo réussi"`
4. **Timeout amélioré** : `"[Instagram] Timeout → 60s dépassé, abandon du conteneur"`

## Points importants respectés

✅ **Aucune modification de la logique Facebook**  
✅ **Aucune dépendance externe ajoutée**  
✅ **Logique webhook n8n non touchée**  
✅ **Comportement images inchangé**  
✅ **Utilise media_type=VIDEO pour les vidéos**  
✅ **Polling optimisé : 3s au lieu de 10s**  
✅ **Timeout respecté : 60s maximum**  

## Test de validation
Le script `/app/test_video_support.py` valide que :
- La fonction de polling utilise bien l'intervalle de 3s
- Les logs sont correctement affichés
- Le timeout fonctionne comme attendu

## Status : ✅ COMPLET
Toutes les spécifications ont été implémentées avec succès dans server.py uniquement.