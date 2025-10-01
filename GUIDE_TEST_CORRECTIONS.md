# 🧪 Guide de Test - Corrections Session 2

## ✅ Corrections Appliquées

### 1. 🎥 Détection Vidéo Facebook Améliorée
- **Problème corrigé**: Vidéos détectées comme images
- **Solution**: Analyse MIME type réelle au lieu de l'URL
- **Formats supportés**: .mp4, .mov, .avi, .wmv, .m4v, .mkv

### 2. 📡 FTP Instagram Ultra-Robuste  
- **Problème corrigé**: Erreur WinError 64 "nom réseau non disponible"
- **Solution**: 4 configurations FTP + retry automatique
- **Retry logic**: Backoff exponentiel 1s → 2s → 4s

### 3. ⏱️ Polling OAuth Optimisé
- **Problème corrigé**: Polling trop fréquent (spam logs)
- **Solution**: Confirmé à 120s (2 minutes)

## 🔬 Tests Automatiques

```bash
# Lancer les tests de validation
cd /app
python test_corrections_session2.py
```

## 📋 Tests Manuels

### Test 1: Publication Vidéo Facebook

1. **Démarrer les services**:
   ```bash
   cd /app/backend
   python server.py
   ```

2. **Tester avec curl**:
   ```bash
   # Upload vidéo .mp4 (sera détectée comme vidéo)
   curl -X POST -F "store=gizmobbs" \
        -F "title=Test Vidéo" \
        -F "url=https://example.com" \
        -F "description=Test description" \
        -F "file=@test_video.mp4" \
        http://localhost:8001/api/webhook
   ```

3. **Vérifier les logs**: Chercher "🎥 CORRECTION: Vidéo détectée par MIME type"

### Test 2: Publication Instagram (FTP)

1. **Tester connexion FTP**:
   ```bash
   curl http://localhost:8001/api/test-ftp
   ```

2. **Publication Instagram avec image**:
   ```bash
   curl -X POST -F "store=gizmobbs" \
        -F "title=Test Instagram" \
        -F "url=https://example.com" \
        -F "description=Test IG" \
        -F "file=@test_image.jpg" \
        http://localhost:8001/api/webhook
   ```

3. **Vérifier logs FTP**: Chercher "[CORRECTION] Tentative FTP" et confirmations d'upload

### Test 3: OAuth Polling

1. **Ouvrir interface**: http://localhost:3000
2. **Ouvrir Console navigateur** (F12)
3. **Observer requêtes OAuth**: Doivent arriver toutes les 2 minutes maximum

## 🎯 Indicateurs de Succès

### ✅ Vidéos Facebook
- Logs montrent "Vidéo détectée par MIME type: video/mp4"
- Endpoint utilisé: `/videos` au lieu de `/photos` ou `/feed`
- Pas d'erreur "média détecté comme image"

### ✅ FTP Instagram  
- Upload réussi avec message "[CORRECTION] Upload FTP réussi"
- Pas d'erreur "WinError 64" ou "nom réseau non disponible"
- URL publique générée correctement (HTTPS)

### ✅ OAuth Polling
- Logs OAuth espacés de 2 minutes minimum
- Pas de spam "oauth-status-complete" toutes les secondes
- Interface responsive sans surcharge réseau

## 🛠️ Dépannage

### Si vidéos encore détectées comme images:
1. Vérifier que le fichier est bien dans `/uploads/`
2. Tester avec différents formats vidéo
3. Consulter logs pour voir quel type MIME est détecté

### Si FTP échoue encore:
1. Tester `/api/test-ftp` pour diagnostic complet
2. Vérifier connectivité réseau vers logicamp.org:21
3. Les 4 configurations FTP seront testées automatiquement

### Si polling encore trop fréquent:
1. Vider cache navigateur (Ctrl+F5)
2. Vérifier onglets multiples ouverts
3. Inspecter Network dans DevTools

## 📊 Statut Final

Les 3 problèmes critiques identifiés ont été corrigés:
- ✅ Détection vidéo Facebook (MIME type)
- ✅ FTP Instagram robuste (retry logic)  
- ✅ Polling OAuth optimisé (120s confirmé)

**Crédits utilisés**: 4/10 (6 crédits restants disponibles)