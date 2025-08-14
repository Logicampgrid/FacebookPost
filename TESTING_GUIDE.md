# Guide de Test - Images Cliquables & Instagram

## 🎯 Problèmes Identifiés et Solutions

### Problème 1 : Images cliquables Facebook
**Symptôme :** Les images ne redirigent pas vers la fiche produit quand on clique dessus sur Facebook

### Problème 2 : Publication Instagram
**Symptôme :** La publication sur Instagram ne fonctionne pas

## 🔧 Corrections Apportées

1. ✅ **Amélioration du téléchargement d'images** (timeout et gestion d'erreurs)
2. ✅ **Validation des URLs d'images clickables** 
3. ✅ **Meilleure gestion des erreurs Instagram**
4. ✅ **Endpoints de test dédiés**

## 🧪 Comment Tester

### Étape 1 : Obtenir un Token Facebook

1. Allez sur [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Sélectionnez **App ID: 5664227323683118**
3. Cliquez sur "Generate Access Token" et sélectionnez "User Token"
4. **IMPORTANT :** Ajoutez ces permissions :
   - `pages_manage_posts`
   - `pages_read_engagement` 
   - `pages_show_list`
   - `business_management`
   - `instagram_content_publish` (pour Instagram)
5. Copiez le token généré

### Étape 2 : Test via Frontend

1. Allez sur http://localhost:3000
2. Sélectionnez "Token manuel (solution temporaire)"
3. Collez votre token Facebook
4. Cliquez sur "Tester le Token"
5. Une fois connecté, essayez de créer des posts avec images

### Étape 3 : Tests API Directs

#### Test de Diagnostic
```bash
curl -X POST "http://localhost:8001/api/test/clickable-instagram" \
-H "Content-Type: application/json" \
-d '{
  "access_token": "VOTRE_TOKEN_ICI"
}'
```

#### Test d'Image Cliquable
```bash
curl -X POST "http://localhost:8001/api/test/post-direct" \
-H "Content-Type: application/json" \
-d '{
  "access_token": "VOTRE_TOKEN_ICI",
  "test_type": "clickable"
}'
```

#### Test Instagram
```bash
curl -X POST "http://localhost:8001/api/test/post-direct" \
-H "Content-Type: application/json" \
-d '{
  "access_token": "VOTRE_TOKEN_ICI", 
  "test_type": "instagram"
}'
```

## 📊 Surveillance des Logs

Pendant les tests, surveillez les logs backend :
```bash
tail -f /var/log/supervisor/backend.out.log
```

## 🔍 Vérifications à Faire

### Pour les Images Cliquables :
1. ✅ Le post est créé sur Facebook
2. ✅ L'image s'affiche correctement  
3. ✅ Cliquer sur l'image redirige vers l'URL du produit
4. ✅ Dans les logs : "✅ Clickable image post created successfully!"

### Pour Instagram :
1. ✅ Le post apparaît sur le compte Instagram
2. ✅ L'image s'affiche correctement
3. ✅ Le caption est présent
4. ✅ Dans les logs : "✅ Instagram post published successfully!"

## ⚠️ Problèmes Possibles et Solutions

### Images Cliquables
- **Si ça ne fonctionne pas :** Vérifiez que l'URL de l'image est accessible publiquement
- **Permission manquante :** Assurez-vous d'avoir `pages_manage_posts`
- **URL du produit invalide :** Vérifiez que l'URL du produit est valide et accessible

### Instagram
- **Erreur de permissions :** Ajoutez `instagram_content_publish` aux permissions
- **Compte non Business :** Le compte Instagram doit être un compte Business
- **Pas connecté à Facebook :** Le compte Instagram doit être connecté à une page Facebook

## 🎯 Tests de Validation

Après correction, testez ces scénarios :

1. **Image cliquable Facebook :**
   - Créer un post avec image
   - Vérifier que cliquer sur l'image redirige
   - Tester sur mobile et desktop

2. **Publication Instagram :**
   - Créer un post avec image
   - Vérifier qu'il apparaît sur Instagram
   - Tester avec et sans légende

3. **Cross-posting :**
   - Publier simultanément sur Facebook et Instagram
   - Vérifier que les deux publications réussissent

## 📈 Résultats Attendus

**✅ SUCCÈS :**
- Images cliquables sur Facebook redirigent correctement
- Publications Instagram apparaissent automatiquement
- Logs montrent "✅ Clickable image post created successfully!"
- Logs montrent "✅ Instagram post published successfully!"

**❌ ÉCHEC :**
- Messages d'erreur dans les logs
- Posts créés mais fonctionnalités ne marchent pas
- Erreurs de permissions ou d'authentification

## 🆘 Support

Si les tests échouent encore après avoir suivi ce guide :
1. Copiez les logs d'erreur complets
2. Vérifiez les permissions du token Facebook
3. Assurez-vous que le compte Instagram est un compte Business connecté à Facebook