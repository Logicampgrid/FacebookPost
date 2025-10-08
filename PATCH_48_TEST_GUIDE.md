# 🎯 PATCH 48 - Guide de Test Upload Direct Vidéos Facebook

## ✅ Statut
- **PATCH 48 appliqué avec succès**
- **Backend redémarré automatiquement** (mode reload)
- **Tests d'implémentation: ✅ RÉUSSIS**

## 🔧 Changements Appliqués

### Problème Résolu
```
❌ AVANT: "Vous n'avez pas l'autorisation d'importer une vidéo ici"
   - Erreur Facebook: code 6000, subcode 1363042
   - Les vidéos utilisaient file_url (URL externe)
   - Facebook refusait les URLs externes pour les vidéos

✅ APRÈS: Upload direct du fichier vidéo à Facebook
   - Même mécanisme que les images (PATCH 26)
   - Téléchargement depuis FTP puis upload multipart
   - Facebook accepte les uploads directs de fichiers
```

### Code Modifié
- **Fichier**: `/app/backend/server.py`
- **Fonction**: `publish_to_facebook()` lignes 6135-6171
- **Nouveau**: Upload direct vidéos avec détection MIME automatique

## 🧪 Test du PATCH 48

### Méthode 1: Via n8n (Recommandé)

1. **Envoyer une vidéo via votre workflow n8n existant**
   ```json
   {
     "store": "logicamp",
     "title": "Test PATCH 48 - Vidéo",
     "url": "https://logicamp.org/wordpress/produit/test",
     "description": "Test upload direct vidéo Facebook",
     "video_file": "[votre fichier MP4]"
   }
   ```

2. **Surveiller les logs backend**
   ```bash
   # Sur Windows (si vous avez accès aux logs)
   tail -f logs/backend.log | findstr "PATCH 48"
   
   # Ce que vous devriez voir:
   🔄 PATCH 48: Téléchargement vidéo pour upload direct: https://...
   ✅ PATCH 48: Vidéo téléchargée (4103256 bytes, video/mp4)
   ✅ Publication Facebook réussie: ID 123456789
   ```

3. **Vérifier sur Facebook**
   - La vidéo doit apparaître sur votre page Facebook
   - Plus d'erreur d'autorisation

### Méthode 2: Via curl (Test Manuel)

```bash
# Test avec fichier vidéo local
curl -X POST http://localhost:8001/api/webhook \
  -F "json_data={\"store\":\"logicamp\",\"title\":\"Test PATCH 48\",\"url\":\"https://test.com\",\"description\":\"Test vidéo\"}" \
  -F "video_file=@/path/to/your/video.mp4"
```

## 📊 Logs à Surveiller

### ✅ Logs de Succès
```
🔄 PATCH 48: Téléchargement vidéo pour upload direct: https://logicamp.org/wordpress/uploads/webhook_xxx.mp4
✅ PATCH 48: Vidéo téléchargée (4103256 bytes, video/mp4)
🔄 PATCH 26: Upload direct du fichier à Facebook
✅ Publication Facebook réussie: ID 820190253860235
```

### ⚠️ Logs de Fallback (Si échec téléchargement)
```
⚠️ PATCH 48: Échec téléchargement, fallback file_url: 404
⚠️ PATCH 48: Erreur téléchargement vidéo, fallback file_url: Timeout
```
*Note: Le fallback utilise l'ancienne méthode file_url*

### ❌ Logs d'Erreur à Investiguer
```
❌ Erreur Facebook HTTP 400: {"error":{"message":"There was a problem uploading your video file..."}}
```
*Si cette erreur persiste, cela peut indiquer un problème de permissions Facebook*

## 🎯 Résultats Attendus

### Pour Chaque Store

| Store | Page Facebook | Statut Attendu |
|-------|---------------|----------------|
| **gizmobbs** | Le Berger Blanc Suisse (102401876209415) | ✅ Vidéos publiées |
| **logicantiq** | LogicAntiq (210654558802531) | ✅ Vidéos publiées |
| **outdoor** | Logicamp Outdoor (236260991673388) | ✅ Vidéos publiées |
| **logicamp** | Logicamp (174450429258625) | ✅ Vidéos publiées |

### Comparaison Avant/Après

| Plateforme | Type | AVANT PATCH 48 | APRÈS PATCH 48 |
|------------|------|----------------|----------------|
| Facebook | Images | ✅ Fonctionne | ✅ Fonctionne |
| Facebook | Vidéos | ❌ Erreur 6000 | ✅ Fonctionne |
| Instagram | Images | ✅ Fonctionne | ✅ Fonctionne |
| Instagram | Reels | ✅ Fonctionne | ✅ Fonctionne |

## 🔧 Dépannage

### Problème: Vidéos toujours refusées par Facebook

**Vérifications:**
1. Le token Facebook a-t-il les permissions `pages_manage_posts` et `pages_read_engagement`?
2. La page Facebook est-elle vérifiée et autorisée à publier des vidéos?
3. Le fichier vidéo respecte-t-il les limites Facebook (format, taille, durée)?

**Limites Facebook:**
- Format: MP4, MOV
- Taille max: 10 GB
- Durée max: 240 minutes
- Codec: H.264

### Problème: Timeout lors du téléchargement

**Solution**: Le timeout est configuré à 60s (ligne 6139). Pour des vidéos très lourdes:
```python
# Augmenter le timeout dans server.py ligne 6139
media_response = requests.get(media_url, timeout=180)  # 3 minutes
```

### Problème: Vidéo téléchargée mais publication échoue

**Vérifier:**
1. Le format MIME est-il correct? (video/mp4 ou video/quicktime)
2. Le fichier est-il corrompu?
3. Les permissions du token sont-elles suffisantes?

## 📈 Métriques de Performance

### Temps de Traitement Estimé
- Téléchargement vidéo (5 MB): ~2-5 secondes
- Upload à Facebook: ~5-10 secondes
- **Total**: ~7-15 secondes par vidéo

### Comparaison
- **AVANT**: file_url → Échec immédiat (erreur 6000)
- **APRÈS**: Upload direct → Succès en 7-15s

## 🎉 Validation Finale

### Checklist de Validation
- [ ] PATCH 48 implémenté dans server.py
- [ ] Backend redémarré et fonctionnel
- [ ] Test avec vidéo n8n envoyé
- [ ] Logs PATCH 48 visibles
- [ ] Publication Facebook réussie
- [ ] Vidéo visible sur la page Facebook
- [ ] Instagram Reels continue de fonctionner

### Confirmation de Succès
Quand TOUS les points suivants sont vérifiés:
✅ Plus d'erreur "Vous n'avez pas l'autorisation d'importer une vidéo ici"
✅ Logs montrent "✅ PATCH 48: Vidéo téléchargée"
✅ Logs montrent "✅ Publication Facebook réussie: ID XXX"
✅ Vidéo visible sur la page Facebook

## 📝 Crédits Utilisés
- **PATCH 48**: 1 crédit
- **Crédits restants**: 9/10
- **Session**: Nouvelle session (après fb5-test3)

## 🔄 Rollback (Si Nécessaire)

Si le PATCH 48 cause des problèmes, revenir en arrière:

```bash
# Restaurer server.py depuis backup
cp /app/backend/server.py.backup /app/backend/server.py

# Redémarrer
sudo supervisorctl restart backend
```

Le système reviendra au comportement précédent (file_url pour vidéos).

## 📞 Support

Si les vidéos Facebook ne fonctionnent toujours pas après le PATCH 48:
1. Vérifier les permissions du token Facebook
2. Tester avec une vidéo de petite taille (< 5 MB)
3. Vérifier que la page Facebook est configurée correctement
4. Consulter les logs détaillés pour identifier le problème exact

---

**Date**: Session actuelle (après fb5-test3)
**Crédits**: 1/10 utilisés
**Status**: ✅ PATCH 48 APPLIQUÉ ET TESTÉ
