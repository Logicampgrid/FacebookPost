import React, { useState, useEffect } from 'react';
import { Instagram, Users, CheckCircle, AlertCircle, Loader, ExternalLink, ArrowRight, Zap } from 'lucide-react';
import axios from 'axios';

const InstagramTunnelSetup = ({ user, onUserConnected, onTunnelReady }) => {
  const [setupStatus, setSetupStatus] = useState('not_connected');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [diagnosis, setDiagnosis] = useState(null);
  const [manualToken, setManualToken] = useState('');
  const [showTokenInput, setShowTokenInput] = useState(false);

  const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    if (user) {
      checkTunnelStatus();
    } else {
      setSetupStatus('not_connected');
    }
  }, [user]);

  const checkTunnelStatus = async () => {
    try {
      setLoading(true);
      
      // Vérifier le diagnostic Instagram complet
      const response = await axios.get(`${API_BASE}/api/debug/instagram-complete-diagnosis`);
      const diagnosisData = response.data;
      
      setDiagnosis(diagnosisData);
      
      if (diagnosisData.instagram_accounts && diagnosisData.instagram_accounts.length > 0) {
        // Vérifier si @logicamp_berger est disponible
        const logicampAccount = diagnosisData.instagram_accounts.find(
          account => account.username === 'logicamp_berger'
        );
        
        if (logicampAccount) {
          setSetupStatus('ready');
          if (onTunnelReady) onTunnelReady(true);
        } else {
          setSetupStatus('instagram_not_found');
        }
      } else {
        setSetupStatus('no_instagram');
      }
      
    } catch (error) {
      console.error('Erreur diagnostic tunnel:', error);
      setSetupStatus('error');
      setError('Erreur lors du diagnostic du tunnel Instagram');
    } finally {
      setLoading(false);
    }
  };

  const handleBusinessManagerLogin = () => {
    setError('');
    setLoading(true);

    // URL de connexion Facebook avec permissions Business Manager étendues
    const redirectUri = encodeURIComponent(window.location.origin + window.location.pathname);
    const scope = 'pages_manage_posts,pages_read_engagement,pages_show_list,business_management,read_insights,instagram_basic,instagram_content_publish';
    
    const facebookAuthUrl = `https://www.facebook.com/v18.0/dialog/oauth?` +
      `client_id=5664227323683118&` +
      `redirect_uri=${redirectUri}&` +
      `scope=${scope}&` +
      `response_type=code&` +
      `state=instagram_tunnel_${Math.random().toString(36).substring(7)}`;
    
    window.location.href = facebookAuthUrl;
  };

  const handleManualTokenLogin = async () => {
    if (!manualToken.trim()) {
      setError('Veuillez saisir un token d\'accès Facebook valide');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      // Utiliser la fonction onUserConnected pour simuler la connexion
      if (onUserConnected) {
        await onUserConnected(manualToken);
      }
      
    } catch (err) {
      console.error('Error with manual token:', err);
      setError(`Erreur lors de la connexion: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const testTunnel = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await axios.post(`${API_BASE}/api/debug/test-instagram-webhook-universal?shop_type=gizmobbs`);
      const result = response.data;
      
      if (result.success) {
        alert('✅ Tunnel Instagram testé avec succès!\nVérifiez @logicamp_berger sur Instagram.');
        setSetupStatus('ready');
        if (onTunnelReady) onTunnelReady(true);
      } else {
        throw new Error(result.error || 'Test du tunnel échoué');
      }
      
    } catch (error) {
      console.error('Erreur test tunnel:', error);
      setError(`Test échoué: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const renderStatus = () => {
    switch (setupStatus) {
      case 'not_connected':
        return (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <Instagram className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Tunnel Instagram Gratuit</h2>
              <p className="text-gray-600">Connectez votre Business Manager pour activer la publication automatique sur Instagram</p>
            </div>
            
            <div className="space-y-4">
              <div className="bg-white rounded-lg p-4 border-l-4 border-green-500">
                <h3 className="font-semibold text-gray-900 mb-2">🎯 Cible : @logicamp_berger</h3>
                <p className="text-sm text-gray-600">Vos publications seront automatiquement postées sur ce compte Instagram</p>
              </div>
              
              <div className="grid md:grid-cols-3 gap-4 text-sm">
                <div className="bg-white rounded p-3 text-center">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <Zap className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="font-medium">Publication automatique</div>
                  <div className="text-gray-500">Via webhook API</div>
                </div>
                <div className="bg-white rounded p-3 text-center">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <Instagram className="w-4 h-4 text-purple-600" />
                  </div>
                  <div className="font-medium">Médias optimisés</div>
                  <div className="text-gray-500">Images & hashtags</div>
                </div>
                <div className="bg-white rounded p-3 text-center">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  </div>
                  <div className="font-medium">Multi-magasins</div>
                  <div className="text-gray-500">5 shops supportés</div>
                </div>
              </div>

              <div className="flex flex-col space-y-3">
                <button
                  onClick={handleBusinessManagerLogin}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2 font-medium"
                >
                  {loading ? (
                    <Loader className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      <Users className="w-5 h-5" />
                      <span>Connecter Business Manager</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
                
                <button
                  onClick={() => setShowTokenInput(!showTokenInput)}
                  className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                >
                  Ou utiliser un token manuel
                </button>
              </div>
            </div>
          </div>
        );

      case 'no_instagram':
        return (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="flex items-center space-x-2 text-yellow-600 mb-4">
              <AlertCircle className="w-5 h-5" />
              <span className="font-semibold">Business Manager connecté - Instagram manquant</span>
            </div>
            
            <div className="bg-white rounded-lg p-4 mb-4">
              <h4 className="font-semibold mb-3">📱 Étapes pour connecter Instagram :</h4>
              <ol className="list-decimal list-inside space-y-2 text-sm">
                <li>Allez sur <a href="https://business.facebook.com" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">Facebook Business Manager</a></li>
                <li>Section "Comptes" → "Instagram"</li>
                <li>Cliquez "Ajouter" et connectez @logicamp_berger</li>
                <li>Assurez-vous que c'est un compte <strong>Instagram Business</strong></li>
                <li>Reconnectez-vous ici</li>
              </ol>
            </div>
            
            <button
              onClick={checkTunnelStatus}
              disabled={loading}
              className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 disabled:opacity-50 flex items-center space-x-2"
            >
              {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Instagram className="w-4 h-4" />}
              <span>Revérifier Instagram</span>
            </button>
          </div>
        );

      case 'instagram_not_found':
        return (
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
            <div className="flex items-center space-x-2 text-orange-600 mb-4">
              <AlertCircle className="w-5 h-5" />
              <span className="font-semibold">@logicamp_berger non trouvé</span>
            </div>
            
            <p className="text-gray-700 mb-4">
              Des comptes Instagram sont connectés, mais @logicamp_berger n'est pas accessible.
            </p>
            
            {diagnosis && diagnosis.instagram_accounts && (
              <div className="bg-white rounded-lg p-4 mb-4">
                <h4 className="font-semibold mb-2">Comptes Instagram trouvés :</h4>
                <ul className="space-y-1 text-sm">
                  {diagnosis.instagram_accounts.map((account, index) => (
                    <li key={index} className="flex items-center space-x-2">
                      <Instagram className="w-3 h-3 text-gray-400" />
                      <span>@{account.username} ({account.name})</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <div className="bg-white rounded-lg p-4 mb-4">
              <h4 className="font-semibold mb-2">💡 Solutions possibles :</h4>
              <ul className="list-disc list-inside space-y-1 text-sm">
                <li>Vérifiez que @logicamp_berger est connecté à une page Facebook</li>
                <li>Assurez-vous d'avoir les permissions sur ce compte</li>
                <li>Connectez-vous avec le bon compte Business Manager</li>
              </ul>
            </div>
            
            <button
              onClick={checkTunnelStatus}
              disabled={loading}
              className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 disabled:opacity-50 flex items-center space-x-2"
            >
              {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Instagram className="w-4 h-4" />}
              <span>Revérifier</span>
            </button>
          </div>
        );

      case 'ready':
        return (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center space-x-2 text-green-600 mb-4">
              <CheckCircle className="w-5 h-5" />
              <span className="font-semibold text-lg">🎉 Tunnel Instagram Actif !</span>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4 mb-6">
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold flex items-center space-x-2 mb-2">
                  <Instagram className="w-4 h-4 text-pink-500" />
                  <span>@logicamp_berger</span>
                </h4>
                <p className="text-sm text-gray-600 mb-2">✅ Connecté et prêt pour publications</p>
                <a
                  href="https://www.instagram.com/logicamp_berger/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-1 text-blue-600 hover:underline text-sm"
                >
                  <span>Voir le profil</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold mb-2">🚀 Endpoint Webhook</h4>
                <p className="text-xs bg-gray-100 p-2 rounded">
                  {API_BASE}/api/webhook
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Stores: gizmobbs, outdoor, logicantiq...
                </p>
              </div>
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={testTunnel}
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2"
              >
                {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                <span>Tester le Tunnel</span>
              </button>
              
              <button
                onClick={checkTunnelStatus}
                disabled={loading}
                className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50"
              >
                Actualiser
              </button>
            </div>
          </div>
        );

      case 'error':
      default:
        return (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center space-x-2 text-red-600 mb-4">
              <AlertCircle className="w-5 h-5" />
              <span className="font-semibold">Erreur Tunnel Instagram</span>
            </div>
            <p className="text-gray-700 mb-4">
              Impossible de vérifier le statut du tunnel Instagram.
            </p>
            <button
              onClick={checkTunnelStatus}
              disabled={loading}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              Réessayer
            </button>
          </div>
        );
    }
  };

  return (
    <div className="max-w-4xl mx-auto">      
      {error && (
        <div className="mb-4 flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {renderStatus()}

      {/* Token manuel */}
      {showTokenInput && setupStatus === 'not_connected' && (
        <div className="mt-4 bg-gray-50 border rounded-lg p-4">
          <h4 className="font-semibold mb-3">🔑 Connexion avec Token Manuel</h4>
          <div className="space-y-3">
            <textarea
              value={manualToken}
              onChange={(e) => setManualToken(e.target.value)}
              placeholder="Collez votre token Facebook Business Manager ici..."
              className="w-full p-3 border border-gray-300 rounded-lg text-sm"
              rows="3"
              disabled={loading}
            />
            <div className="text-xs text-blue-600 space-y-1">
              <p>📋 <strong>Obtenir un token :</strong></p>
              <p>1. Allez sur <a href="https://developers.facebook.com/tools/explorer/" target="_blank" rel="noopener noreferrer" className="underline">Graph API Explorer</a></p>
              <p>2. App: 5664227323683118</p>
              <p>3. Permissions: business_management, pages_manage_posts, instagram_content_publish</p>
            </div>
            <button
              onClick={handleManualTokenLogin}
              disabled={loading || !manualToken.trim()}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
            >
              {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Users className="w-4 h-4" />}
              <span>Connecter avec Token</span>
            </button>
          </div>
        </div>
      )}

      {/* Guide d'utilisation */}
      {setupStatus === 'ready' && (
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-3">📖 Guide d'utilisation du Tunnel</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-white rounded p-4">
              <h4 className="font-medium mb-2">🌐 Via Webhook API</h4>
              <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto">
{`curl -X POST "${API_BASE}/api/webhook" \\
  -F "image=@image.jpg" \\
  -F 'json_data={"title":"Mon produit","description":"Description","url":"https://site.com","store":"gizmobbs"}'`}
              </pre>
            </div>
            
            <div className="bg-white rounded p-4">
              <h4 className="font-medium mb-2">🖥️ Via Interface Web</h4>
              <p className="text-sm text-gray-600">
                Utilisez l'onglet "Créer un Post" pour publier manuellement sur Instagram via l'interface.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InstagramTunnelSetup;