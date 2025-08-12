import React, { useEffect, useState } from 'react';
import { Users, AlertCircle } from 'lucide-react';
import axios from 'axios';
import ConnectionStatus from './ConnectionStatus';

const FacebookLogin = ({ onLogin, loading }) => {
  const [error, setError] = useState('');
  const [loginMethod, setLoginMethod] = useState('redirect'); // Default to redirect
  const [exchangingCode, setExchangingCode] = useState(false);
  const [manualToken, setManualToken] = useState('');
  const [showManualTokenInput, setShowManualTokenInput] = useState(false);

  const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

  // Check for Facebook login redirect response
  useEffect(() => {
    const checkFacebookRedirectResponse = async () => {
      // Check if we're returning from Facebook redirect
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const error = urlParams.get('error');
      const errorDescription = urlParams.get('error_description');
      
      if (error) {
        setError(errorDescription || 'Connexion Facebook annulée ou échouée');
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
        return;
      }
      
      if (code) {
        // We have an authorization code, exchange it for access token via backend
        await exchangeCodeForToken(code);
        return;
      }
    };
    
    checkFacebookRedirectResponse();
  }, []);

  const exchangeCodeForToken = async (code) => {
    try {
      setExchangingCode(true);
      setError('');
      
      const redirectUri = window.location.origin + window.location.pathname;
      
      const response = await axios.post(`${API_BASE}/api/auth/facebook/exchange-code`, {
        code: code,
        redirect_uri: redirectUri
      });
      
      if (response.data && response.data.user) {
        onLogin(response.data.access_token);
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
      } else {
        setError('Erreur lors de l\'authentification');
      }
      
    } catch (err) {
      console.error('Error exchanging code for token:', err);
      const errorMsg = err.response?.data?.detail || 'Erreur lors de la connexion Facebook';
      setError(errorMsg);
    } finally {
      setExchangingCode(false);
    }
  };

  const detectPopupBlocker = () => {
    try {
      const popup = window.open('', 'popup', 'width=1,height=1');
      if (!popup || popup.closed || typeof popup.closed === 'undefined') {
        return true; // Popup blocked
      }
      popup.close();
      return false; // Popup not blocked
    } catch (e) {
      return true; // Popup blocked
    }
  };

  const handleFacebookLoginPopup = () => {
    if (loading || exchangingCode) return;
    setError('');
    
    // Check if FB SDK is available
    if (!window.FB) {
      setError('Facebook SDK non disponible. Utilisez la méthode de redirection.');
      return;
    }
    
    // Check if popups are blocked
    if (detectPopupBlocker()) {
      setError('Les popups sont bloquées. Utilisez la méthode de redirection.');
      return;
    }
    
    window.FB.login((response) => {
      if (response.authResponse) {
        onLogin(response.authResponse.accessToken);
      } else if (response.status === 'not_authorized') {
        setError('Vous devez autoriser l\'application pour continuer');
      } else {
        setError('Connexion Facebook annulée ou échouée');
      }
    }, {
      scope: 'pages_manage_posts,pages_read_engagement,pages_show_list,business_management,read_insights'
    });
  };

  const handleFacebookLoginRedirect = () => {
    if (loading || exchangingCode) return;
    setError('');
    
    const redirectUri = window.location.origin + window.location.pathname;
    const facebookAuthUrl = `https://www.facebook.com/v18.0/dialog/oauth?` +
      `client_id=5664227323683118&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `scope=pages_manage_posts,pages_read_engagement,pages_show_list&` +
      `response_type=code&` +
      `state=${Math.random().toString(36).substring(7)}`;
    
    window.location.href = facebookAuthUrl;
  };

  const handleLogin = () => {
    if (loginMethod === 'popup') {
      handleFacebookLoginPopup();
    } else if (loginMethod === 'manual') {
      handleManualTokenLogin();
    } else {
      handleFacebookLoginRedirect();
    }
  };

  const handleManualTokenLogin = async () => {
    if (!manualToken.trim()) {
      setError('Veuillez saisir un token d\'accès Facebook valide');
      return;
    }

    try {
      setExchangingCode(true);
      setError('');
      
      console.log('Testing token:', manualToken.substring(0, 20) + '...');
      
      // Test the token first with better error handling
      const testResponse = await fetch(`${API_BASE}/api/debug/facebook-token/${encodeURIComponent(manualToken)}`);
      
      if (!testResponse.ok) {
        throw new Error(`HTTP ${testResponse.status}: ${testResponse.statusText}`);
      }
      
      const testData = await testResponse.json();
      console.log('Token validation response:', testData);
      
      if (testData.status !== 'valid') {
        const errorMessage = testData.error?.error?.message || 
                            testData.error?.message || 
                            'Token expiré ou incorrect';
        setError(`Token Facebook invalide: ${errorMessage}`);
        return;
      }

      console.log('Token valid, proceeding with login...');
      // Login with the token
      onLogin(manualToken);
      
    } catch (err) {
      console.error('Error with manual token:', err);
      if (err.message.includes('HTTP')) {
        setError(`Erreur de connexion: ${err.message}`);
      } else if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError('Impossible de se connecter au serveur. Vérifiez que le backend est accessible.');
      } else {
        setError(`Erreur lors de la validation du token: ${err.message}`);
      }
    } finally {
      setExchangingCode(false);
    }
  };

  const isLoading = loading || exchangingCode;

  return (
    <div className="space-y-4">
      {/* Connection Status Check */}
      <ConnectionStatus API_BASE={API_BASE} />
      
      {error && (
        <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}
      
      {exchangingCode && (
        <div className="flex items-center justify-center space-x-2 p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-700">
          <div className="spinner" />
          <span className="text-sm">Authentification en cours...</span>
        </div>
      )}
      
      {/* Login Method Selection */}
      <div className="space-y-2">
        <label className="text-sm text-gray-600">Méthode de connexion :</label>
        <div className="space-y-2">
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              value="redirect"
              checked={loginMethod === 'redirect'}
              onChange={(e) => setLoginMethod(e.target.value)}
              className="text-facebook-primary"
              disabled={isLoading}
            />
            <span className="text-sm">Redirection (nécessite configuration domaine)</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              value="popup"
              checked={loginMethod === 'popup'}
              onChange={(e) => setLoginMethod(e.target.value)}
              className="text-facebook-primary"
              disabled={isLoading}
            />
            <span className="text-sm">Popup</span>
          </label>
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              value="manual"
              checked={loginMethod === 'manual'}
              onChange={(e) => setLoginMethod(e.target.value)}
              className="text-facebook-primary"
              disabled={isLoading}
            />
            <span className="text-sm">Token manuel (solution temporaire)</span>
          </label>
        </div>
      </div>

      {/* Manual Token Input */}
      {loginMethod === 'manual' && (
        <div className="space-y-2">
          <label className="text-sm text-gray-600">
            Token d'accès Facebook :
          </label>
          <textarea
            value={manualToken}
            onChange={(e) => setManualToken(e.target.value)}
            placeholder="Collez votre token Facebook ici..."
            className="w-full p-2 border border-gray-300 rounded-lg text-sm"
            rows="3"
            disabled={isLoading}
          />
          <div className="text-xs text-blue-600 space-y-1">
            <p>📋 <strong>Comment obtenir un token :</strong></p>
            <p>1. Allez sur <a href="https://developers.facebook.com/tools/explorer/" target="_blank" rel="noopener noreferrer" className="underline">Facebook Graph API Explorer</a></p>
            <p>2. Sélectionnez App ID: 5664227323683118</p>
            <p>3. Générez un "User Access Token"</p>
            <p>4. Ajoutez les permissions: pages_manage_posts, pages_read_engagement, pages_show_list</p>
            <p>5. Copiez le token généré et collez-le ci-dessus</p>
            <div className="mt-2">
              <a 
                href="https://developers.facebook.com/tools/explorer/?method=GET&path=me&version=v18.0" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-block bg-blue-600 text-white px-3 py-1 text-xs rounded hover:bg-blue-700 transition-colors"
              >
                🚀 Ouvrir Graph API Explorer
              </a>
            </div>
          </div>
        </div>
      )}

      <button
        onClick={handleLogin}
        disabled={isLoading || (loginMethod === 'manual' && !manualToken.trim())}
        className="facebook-button w-full flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <>
            <div className="spinner" />
            <span>{exchangingCode ? 'Authentification...' : 'Connexion en cours...'}</span>
          </>
        ) : (
          <>
            <Users className="w-5 h-5" />
            <span>
              {loginMethod === 'manual' ? 'Tester le Token' : 'Se connecter avec Facebook'}
            </span>
          </>
        )}
      </button>
      
      <div className="text-xs text-gray-500 text-center">
        {loginMethod === 'redirect' 
          ? '⚠️ Nécessite configuration du domaine dans Facebook Developer Console'
          : loginMethod === 'popup'
          ? 'Une popup Facebook s\'ouvrira pour la connexion'
          : 'Solution temporaire avec token manuel'
        }
      </div>
    </div>
  );
};

export default FacebookLogin;