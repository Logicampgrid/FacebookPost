import React, { useEffect, useState } from 'react';
import { Users, AlertCircle } from 'lucide-react';
import axios from 'axios';

const FacebookLogin = ({ onLogin, loading }) => {
  const [error, setError] = useState('');
  const [loginMethod, setLoginMethod] = useState('redirect'); // Default to redirect
  const [exchangingCode, setExchangingCode] = useState(false);

  const API_BASE = process.env.REACT_APP_BACKEND_URL;

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
      scope: 'pages_manage_posts,pages_read_engagement,pages_show_list'
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
    } else {
      handleFacebookLoginRedirect();
    }
  };

  const isLoading = loading || exchangingCode;

  return (
    <div className="space-y-4">
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
        <div className="flex space-x-4">
          <label className="flex items-center space-x-2">
            <input
              type="radio"
              value="redirect"
              checked={loginMethod === 'redirect'}
              onChange={(e) => setLoginMethod(e.target.value)}
              className="text-facebook-primary"
              disabled={isLoading}
            />
            <span className="text-sm">Redirection (recommandé)</span>
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
        </div>
      </div>

      <button
        onClick={handleLogin}
        disabled={isLoading}
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
            <span>Se connecter avec Facebook</span>
          </>
        )}
      </button>
      
      <div className="text-xs text-gray-500 text-center">
        {loginMethod === 'redirect' 
          ? 'Vous serez redirigé vers Facebook pour vous connecter'
          : 'Une popup Facebook s\'ouvrira pour la connexion'
        }
      </div>
    </div>
  );
};

export default FacebookLogin;