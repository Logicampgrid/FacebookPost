## Comment Obtenir un Token Facebook Valide

### Option A: Via Facebook Developers Console
1. Allez sur https://developers.facebook.com/tools/explorer/
2. Sélectionnez votre App ID: 5664227323683118
3. Générez un User Access Token
4. Ajoutez les permissions: pages_manage_posts,pages_read_engagement,pages_show_list
5. Copiez le token généré

### Option B: Via l'Application (Recommandé)
1. Ouvrez http://localhost:3000
2. Utilisez le bouton "Se connecter avec Facebook"
3. La méthode de redirection fonctionne dans tous les environnements

### Option C: URL de Test Direct
https://www.facebook.com/v18.0/dialog/oauth?client_id=5664227323683118&redirect_uri=http://localhost:3000&scope=pages_manage_posts,pages_read_engagement,pages_show_list&response_type=token

### Tester un Nouveau Token
Une fois que vous avez un nouveau token, testez-le avec:
curl "http://localhost:8001/api/debug/facebook-token/VOTRE_NOUVEAU_TOKEN"