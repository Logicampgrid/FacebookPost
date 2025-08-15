import React, { useState } from 'react';
import { CheckCircle, XCircle, RefreshCw, Eye, EyeOff, Facebook } from 'lucide-react';

const FacebookConnectionTest = ({ API_BASE }) => {
  const [token, setToken] = useState('');
  const [showToken, setShowToken] = useState(false);
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState(null);

  const testFacebookToken = async () => {
    if (!token.trim()) {
      setResult({
        success: false,
        message: 'Veuillez saisir un token d\'accès Facebook',
        details: null
      });
      return;
    }

    setTesting(true);
    setResult(null);

    try {
      // Test 1: Direct Facebook API call
      console.log('Testing Facebook token...');
      const fbResponse = await fetch(`https://graph.facebook.com/v18.0/me?access_token=${token}&fields=id,name,email`);
      const fbData = await fbResponse.json();

      if (fbData.error) {
        throw new Error(`Facebook API Error: ${fbData.error.message} (Code: ${fbData.error.code})`);
      }

      // Test 2: Backend authentication
      const backendResponse = await fetch(`${API_BASE}/api/auth/facebook`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          access_token: token
        })
      });

      const backendData = await backendResponse.json();

      if (!backendResponse.ok) {
        throw new Error(`Backend Auth Error: ${backendData.detail || 'Erreur inconnue'}`);
      }

      setResult({
        success: true,
        message: 'Token Facebook valide et authentification réussie',
        details: {
          facebook_user: fbData,
          backend_auth: backendData,
          business_managers: backendData.user?.business_managers?.length || 0,
          pages: backendData.user?.facebook_pages?.length || 0,
          instagram_accounts: backendData.total_instagram_accounts || 0
        }
      });

    } catch (error) {
      console.error('Facebook token test error:', error);
      setResult({
        success: false,
        message: error.message,
        details: { error: error.message }
      });
    } finally {
      setTesting(false);
    }
  };

  const generateTestToken = () => {
    const fbAppId = '5664227323683118';
    const redirectUri = encodeURIComponent(window.location.origin);
    const scope = encodeURIComponent('pages_manage_posts,pages_read_engagement,pages_show_list,groups_access_member_info,instagram_basic,instagram_content_publish,business_management');
    
    const authUrl = `https://www.facebook.com/v18.0/dialog/oauth?client_id=${fbAppId}&redirect_uri=${redirectUri}&scope=${scope}&response_type=token`;
    
    window.open(authUrl, 'facebook-auth', 'width=600,height=600');
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2">
        <Facebook className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-800">Test de Connexion Facebook</h3>
      </div>

      <div className="space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Token d'accès Facebook
          </label>
          <div className="relative">
            <input
              type={showToken ? 'text' : 'password'}
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Collez votre token d'accès Facebook ici..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
            />
            <button
              type="button"
              onClick={() => setShowToken(!showToken)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              {showToken ? (
                <EyeOff className="w-4 h-4 text-gray-400" />
              ) : (
                <Eye className="w-4 h-4 text-gray-400" />
              )}
            </button>
          </div>
        </div>

        <div className="flex space-x-3">
          <button
            onClick={testFacebookToken}
            disabled={testing || !token.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${testing ? 'animate-spin' : ''}`} />
            <span>Tester le Token</span>
          </button>
          
          <button
            onClick={generateTestToken}
            className="px-4 py-2 bg-facebook-primary text-white rounded hover:bg-blue-700 flex items-center space-x-2"
          >
            <Facebook className="w-4 h-4" />
            <span>Générer un Token</span>
          </button>
        </div>
      </div>

      {result && (
        <div className={`p-4 rounded-lg border ${
          result.success 
            ? 'border-green-200 bg-green-50' 
            : 'border-red-200 bg-red-50'
        }`}>
          <div className="flex items-start space-x-3">
            {result.success ? (
              <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
            ) : (
              <XCircle className="w-5 h-5 text-red-500 mt-0.5" />
            )}
            <div className="flex-1">
              <p className={`font-medium ${
                result.success ? 'text-green-800' : 'text-red-800'
              }`}>
                {result.message}
              </p>
              
              {result.success && result.details && (
                <div className="mt-3 space-y-2">
                  <div className="text-sm text-green-700">
                    <strong>Utilisateur Facebook:</strong> {result.details.facebook_user.name} ({result.details.facebook_user.id})
                  </div>
                  <div className="text-sm text-green-700">
                    <strong>Business Managers:</strong> {result.details.business_managers}
                  </div>
                  <div className="text-sm text-green-700">
                    <strong>Pages Facebook:</strong> {result.details.pages}
                  </div>
                  <div className="text-sm text-green-700">
                    <strong>Comptes Instagram:</strong> {result.details.instagram_accounts}
                  </div>
                </div>
              )}

              {!result.success && result.details && (
                <div className="mt-2 text-sm text-red-700 bg-red-100 p-2 rounded">
                  <strong>Détails de l'erreur:</strong><br />
                  {result.details.error}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="text-sm text-gray-500 bg-gray-50 p-3 rounded">
        <strong>Instructions:</strong>
        <ol className="list-decimal list-inside mt-1 space-y-1">
          <li>Cliquez sur "Générer un Token" pour obtenir un token d'accès Facebook</li>
          <li>Autorisez l'application à accéder à vos pages et groupes Facebook</li>
          <li>Copiez le token depuis l'URL de redirection (après #access_token=)</li>
          <li>Collez le token dans le champ ci-dessus et cliquez sur "Tester le Token"</li>
        </ol>
      </div>
    </div>
  );
};

export default FacebookConnectionTest;