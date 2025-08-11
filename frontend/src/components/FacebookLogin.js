import React from 'react';
import { Users } from 'lucide-react';

const FacebookLogin = ({ onLogin, loading }) => {
  const handleFacebookLogin = () => {
    if (loading) return;
    
    window.FB.login((response) => {
      if (response.authResponse) {
        onLogin(response.authResponse.accessToken);
      } else {
        console.log('User cancelled login or did not fully authorize.');
      }
    }, {
      scope: 'pages_manage_posts,pages_read_engagement,pages_show_list,publish_to_groups'
    });
  };

  return (
    <button
      onClick={handleFacebookLogin}
      disabled={loading}
      className="facebook-button w-full flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {loading ? (
        <>
          <div className="spinner" />
          <span>Connexion en cours...</span>
        </>
      ) : (
        <>
          <Users className="w-5 h-5" />
          <span>Se connecter avec Facebook</span>
        </>
      )}
    </button>
  );
};

export default FacebookLogin;