import React, { useState, useEffect } from 'react';
import { Instagram, Users, CheckCircle, AlertCircle, Loader, ExternalLink, Settings, Zap, Facebook } from 'lucide-react';

const LogicampBergerConnector = ({ user, onConnectionComplete }) => {
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [platforms, setPlatforms] = useState({
    facebook: { connected: false, page: null },
    instagram: { connected: false, account: null }
  });
  const [testResult, setTestResult] = useState(null);

  const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    if (user) {
      checkLogicampConnection();
    }
  }, [user]);

  const checkLogicampConnection = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Vérifier la connexion à @logicamp_berger
      const response = await fetch(`${API_BASE}/api/logicamp-berger/status`, {
        method: 'GET'
      });
      
      const data = await response.json();
      
      if (data.success) {
        setPlatforms(data.platforms);
        
        // Déterminer le statut global
        if (data.platforms.facebook.connected && data.platforms.instagram.connected) {
          setConnectionStatus('fully_connected');
        } else if (data.platforms.facebook.connected || data.platforms.instagram.connected) {
          setConnectionStatus('partially_connected');
        } else {
          setConnectionStatus('not_connected');
        }
        
        if (onConnectionComplete && data.platforms.facebook.connected) {
          onConnectionComplete(data.platforms);
        }
      } else {
        setError(data.error || 'Erreur lors de la vérification de la connexion');
        setConnectionStatus('error');
      }
      
    } catch (err) {
      console.error('Erreur vérification connexion:', err);
      setError('Impossible de vérifier la connexion à @logicamp_berger');
      setConnectionStatus('error');
    } finally {
      setLoading(false);
    }
  };

  const establishConnection = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Lancer la procédure de connexion automatique
      const response = await fetch(`${API_BASE}/api/logicamp-berger/connect`, {
        method: 'POST'
      });
      
      const data = await response.json();
      
      if (data.success) {
        setPlatforms(data.platforms);
        setConnectionStatus(data.status);
        
        if (onConnectionComplete) {
          onConnectionComplete(data.platforms);
        }
      } else {
        setError(data.error || 'Erreur lors de la connexion');
      }
      
    } catch (err) {
      console.error('Erreur connexion:', err);
      setError('Impossible de se connecter à @logicamp_berger');
    } finally {
      setLoading(false);
    }
  };

  const testWebhookPublication = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Tester la publication webhook sur les deux plateformes
      const response = await fetch(`${API_BASE}/api/logicamp-berger/test-webhook`, {
        method: 'POST'
      });
      
      const result = await response.json();
      setTestResult(result);
      
    } catch (err) {
      console.error('Erreur test webhook:', err);
      setTestResult({
        success: false,
        error: 'Erreur lors du test de publication'
      });
    } finally {
      setLoading(false);
    }
  };

  const renderConnectionStatus = () => {
    switch (connectionStatus) {
      case 'checking':
        return (
          <div className="flex items-center space-x-2 text-blue-600">
            <Loader className="w-5 h-5 animate-spin" />
            <span>Vérification de la connexion @logicamp_berger...</span>
          </div>
        );

      case 'not_connected':
        return (
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
            <div className="flex items-center space-x-2 text-orange-600 mb-4">
              <AlertCircle className="w-5 h-5" />
              <span className="font-semibold">Connexion @logicamp_berger requise</span>
            </div>
            
            <p className="text-gray-700 mb-4">
              Pour publier simultanément sur Facebook et Instagram via webhook, connectez-vous à @logicamp_berger.
            </p>
            
            <div className="grid md:grid-cols-2 gap-4 mb-6">
              <div className="bg-white rounded-lg p-4 border-l-4 border-blue-500">
                <h4 className="font-semibold flex items-center space-x-2 mb-2">
                  <Facebook className="w-4 h-4 text-blue-600" />
                  <span>Page Facebook</span>
                </h4>
                <p className="text-sm text-gray-600">Le Berger Blanc Suisse</p>
                <p className="text-xs text-gray-500">Publication via API Facebook</p>
              </div>
              
              <div className="bg-white rounded-lg p-4 border-l-4 border-pink-500">
                <h4 className="font-semibold flex items-center space-x-2 mb-2">
                  <Instagram className="w-4 h-4 text-pink-600" />
                  <span>Instagram Business</span>
                </h4>
                <p className="text-sm text-gray-600">@logicamp_berger</p>
                <p className="text-xs text-gray-500">Publication via API Instagram</p>
              </div>
            </div>
            
            <button
              onClick={establishConnection}
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-500 to-pink-500 text-white py-3 px-4 rounded-lg hover:from-blue-600 hover:to-pink-600 disabled:opacity-50 flex items-center justify-center space-x-2 font-medium"
            >
              {loading ? (
                <Loader className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Settings className="w-5 h-5" />
                  <span>Établir la connexion @logicamp_berger</span>
                </>
              )}
            </button>
          </div>
        );

      case 'partially_connected':
        return (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="flex items-center space-x-2 text-yellow-600 mb-4">
              <AlertCircle className="w-5 h-5" />
              <span className="font-semibold">Connexion partielle</span>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              <div className={`bg-white rounded-lg p-4 border-l-4 ${
                platforms.facebook.connected ? 'border-green-500' : 'border-red-500'
              }`}>
                <h4 className="font-semibold flex items-center space-x-2 mb-2">
                  <Facebook className="w-4 h-4 text-blue-600" />
                  <span>Facebook</span>
                  {platforms.facebook.connected ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-red-500" />
                  )}
                </h4>
                <p className="text-sm text-gray-600">
                  {platforms.facebook.connected ? 
                    platforms.facebook.page?.name || 'Page connectée' : 
                    'Page non connectée'
                  }
                </p>
              </div>
              
              <div className={`bg-white rounded-lg p-4 border-l-4 ${
                platforms.instagram.connected ? 'border-green-500' : 'border-red-500'
              }`}>
                <h4 className="font-semibold flex items-center space-x-2 mb-2">
                  <Instagram className="w-4 h-4 text-pink-600" />
                  <span>Instagram</span>
                  {platforms.instagram.connected ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-red-500" />
                  )}
                </h4>
                <p className="text-sm text-gray-600">
                  {platforms.instagram.connected ? 
                    `@${platforms.instagram.account?.username || 'logicamp_berger'}` : 
                    '@logicamp_berger (non connecté)'
                  }
                </p>
              </div>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded p-4 mb-4">
              <p className="text-blue-800 text-sm">
                <strong>Publication possible :</strong> {platforms.facebook.connected ? 'Facebook' : ''} 
                {platforms.facebook.connected && platforms.instagram.connected ? ' + ' : ''}
                {platforms.instagram.connected ? 'Instagram' : ''}
              </p>
            </div>
            
            <button
              onClick={establishConnection}
              disabled={loading}
              className="w-full bg-yellow-600 text-white py-2 px-4 rounded-lg hover:bg-yellow-700 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {loading ? (
                <Loader className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <Settings className="w-4 h-4" />
                  <span>Compléter la connexion</span>
                </>
              )}
            </button>
          </div>
        );

      case 'fully_connected':
        return (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center space-x-2 text-green-600 mb-4">
              <CheckCircle className="w-5 h-5" />
              <span className="font-semibold text-lg">🎉 @logicamp_berger Connecté !</span>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4 mb-6">
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold flex items-center space-x-2 mb-2">
                  <Facebook className="w-4 h-4 text-blue-600" />
                  <span>Page Facebook</span>
                  <CheckCircle className="w-4 h-4 text-green-500" />
                </h4>
                <p className="text-sm text-gray-600 mb-1">{platforms.facebook.page?.name}</p>
                <p className="text-xs text-green-600">✅ Publication active</p>
              </div>
              
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-semibold flex items-center space-x-2 mb-2">
                  <Instagram className="w-4 h-4 text-pink-600" />
                  <span>Instagram Business</span>
                  <CheckCircle className="w-4 h-4 text-green-500" />
                </h4>
                <p className="text-sm text-gray-600 mb-1">@{platforms.instagram.account?.username}</p>
                <p className="text-xs text-green-600">✅ Publication active</p>
                <a
                  href={`https://www.instagram.com/${platforms.instagram.account?.username}/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-1 text-blue-600 hover:underline text-xs mt-1"
                >
                  <span>Voir le profil</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <h4 className="font-semibold text-blue-900 mb-2">🚀 Publication Webhook Multi-Plateformes</h4>
              <div className="space-y-2 text-sm">
                <p className="text-blue-800">
                  <strong>Endpoint :</strong> <code className="bg-white px-2 py-1 rounded">{API_BASE}/api/webhook</code>
                </p>
                <p className="text-blue-800">
                  <strong>Shop Type :</strong> <code className="bg-white px-2 py-1 rounded">"gizmobbs"</code>
                </p>
                <div className="bg-white rounded p-3 mt-3">
                  <p className="text-green-800 font-medium mb-1">✅ Publication simultanée activée :</p>
                  <ul className="text-sm space-y-1">
                    <li>• Facebook : Page "Le Berger Blanc Suisse"</li>
                    <li>• Instagram : @logicamp_berger</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={testWebhookPublication}
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2"
              >
                {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                <span>Tester Publication Multi-Plateformes</span>
              </button>
              
              <button
                onClick={checkLogicampConnection}
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
              <span className="font-semibold">Erreur de connexion</span>
            </div>
            <p className="text-gray-700 mb-4">
              Impossible de vérifier ou d'établir la connexion à @logicamp_berger.
            </p>
            <button
              onClick={checkLogicampConnection}
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
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-pink-500 rounded-full flex items-center justify-center">
            <Instagram className="w-5 h-5 text-white" />
          </div>
          <span>Connexion @logicamp_berger</span>
        </h2>
        <p className="text-gray-600">
          Configuration pour publication simultanée Facebook + Instagram via webhook
        </p>
      </div>

      {error && (
        <div className="mb-4 flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {renderConnectionStatus()}

      {/* Résultat du test */}
      {testResult && (
        <div className={`mt-6 border rounded-lg p-4 ${
          testResult.success 
            ? 'bg-green-50 border-green-200' 
            : 'bg-red-50 border-red-200'
        }`}>
          <h4 className={`font-semibold mb-2 ${
            testResult.success ? 'text-green-900' : 'text-red-900'
          }`}>
            {testResult.success ? '✅ Test Multi-Plateformes Réussi !' : '❌ Test Multi-Plateformes Échoué'}
          </h4>
          
          {testResult.success && testResult.results && (
            <div className="space-y-3">
              {testResult.results.facebook && (
                <div className="bg-white rounded p-3">
                  <p className="font-medium text-blue-800">Facebook</p>
                  <p className="text-sm text-gray-600">
                    Publié sur : {testResult.results.facebook.page_name}
                  </p>
                  {testResult.results.facebook.post_url && (
                    <a 
                      href={testResult.results.facebook.post_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-sm"
                    >
                      Voir le post Facebook
                    </a>
                  )}
                </div>
              )}
              
              {testResult.results.instagram && (
                <div className="bg-white rounded p-3">
                  <p className="font-medium text-pink-800">Instagram</p>
                  <p className="text-sm text-gray-600">
                    Publié sur : @{testResult.results.instagram.username}
                  </p>
                </div>
              )}
            </div>
          )}
          
          <pre className="text-xs bg-white border rounded p-2 mt-2 overflow-auto max-h-40">
            {JSON.stringify(testResult, null, 2)}
          </pre>
        </div>
      )}

      {/* Guide webhook */}
      {connectionStatus === 'fully_connected' && (
        <div className="mt-6 bg-gray-50 border rounded-lg p-6">
          <h3 className="font-semibold text-gray-900 mb-3">📖 Guide Webhook Multi-Plateformes</h3>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-white rounded p-4">
              <h4 className="font-medium mb-2">🌐 Requête Webhook</h4>
              <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto">
{`curl -X POST "${API_BASE}/api/webhook" \\
  -F "image=@produit.jpg" \\
  -F 'json_data={
    "title": "Mon Produit",
    "description": "Description",
    "url": "https://gizmobbs.com/produit",
    "store": "gizmobbs"
  }'`}
              </pre>
            </div>
            
            <div className="bg-white rounded p-4">
              <h4 className="font-medium mb-2">📱 Résultat</h4>
              <ul className="text-sm space-y-1">
                <li>• Publication Facebook automatique</li>
                <li>• Publication Instagram simultanée</li>
                <li>• Images optimisées pour chaque plateforme</li>
                <li>• Liens et hashtags adaptés</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LogicampBergerConnector;