import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, Calendar, Send, Building2, Instagram, MessageSquare, Package } from 'lucide-react';
import PostCreator from './components/PostCreator';
import PostList from './components/PostList';
import FacebookLogin from './components/FacebookLogin';
import PlatformSelector from './components/PlatformSelector';
import BusinessManagerSelector from './components/BusinessManagerSelector';
import WebhookHistory from './components/WebhookHistory';
import ConnectionDiagnostic from './components/ConnectionDiagnostic';
import FacebookConnectionTest from './components/FacebookConnectionTest';
import InstagramDiagnostics from './components/InstagramDiagnostics';
import InstagramSetupGuide from './components/InstagramSetupGuide';
import ImageOrientationTest from './components/ImageOrientationTest';
import LogicampBergerSetup from './components/LogicampBergerSetup';
import LogicampBergerConnector from './components/LogicampBergerConnector';
import InstagramTunnelSetup from './components/InstagramTunnelSetup';
import TunnelStatusWidget from './components/TunnelStatusWidget';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

function App() {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [selectedBusinessManager, setSelectedBusinessManager] = useState(null);
  const [allPlatforms, setAllPlatforms] = useState({
    business_pages: [],
    business_groups: [],
    business_instagram: [],
    personal_pages: [],
    personal_groups: []
  });
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('setup');
  const [fbInitialized, setFbInitialized] = useState(false);

  // Initialize Facebook SDK with better error handling
  useEffect(() => {
    const initFacebookSDK = () => {
      // Check if FB SDK is already loaded
      if (window.FB) {
        initFB();
        return;
      }

      // Wait for FB SDK to load
      window.fbAsyncInit = function() {
        try {
          window.FB.init({
            appId: '5664227323683118',
            cookie: true,
            xfbml: true,
            version: 'v18.0'
          });
          
          // Check login status
          window.FB.getLoginStatus((response) => {
            console.log('FB Login Status:', response.status);
            setFbInitialized(true);
          });
          
        } catch (error) {
          console.error('Facebook SDK initialization error:', error);
          setFbInitialized(true); // Still allow the app to function
        }
      };

      // Fallback if FB SDK doesn't load
      setTimeout(() => {
        if (!window.FB && !fbInitialized) {
          console.warn('Facebook SDK failed to load, using redirect method only');
          setFbInitialized(true);
        }
      }, 5000);
    };

    const initFB = () => {
      try {
        window.FB.init({
          appId: '5664227323683118',
          cookie: true,
          xfbml: true,
          version: 'v18.0'
        });
        setFbInitialized(true);
      } catch (error) {
        console.error('Facebook SDK init error:', error);
        setFbInitialized(true);
      }
    };

    initFacebookSDK();
  }, [fbInitialized]);

  // Load posts when user is authenticated
  useEffect(() => {
    if (user) {
      loadPosts();
      loadUserPlatforms();
    }
  }, [user]);

  // Update platforms when business manager selection changes
  useEffect(() => {
    if (user && selectedBusinessManager) {
      const businessManagerData = user.business_managers?.find(bm => bm.id === selectedBusinessManager.id);
      if (businessManagerData) {
        setAllPlatforms(prev => ({
          ...prev,
          business_pages: businessManagerData.pages || [],
          business_groups: businessManagerData.groups || [],
          business_instagram: businessManagerData.instagram_accounts || []
        }));
        
        // Clear selected platform if it's not from the current business manager
        if (selectedPlatform && selectedPlatform._sourceType === 'business') {
          const platformExists = 
            (businessManagerData.pages?.some(p => p.id === selectedPlatform.id)) ||
            (businessManagerData.groups?.some(g => g.id === selectedPlatform.id)) ||
            (businessManagerData.instagram_accounts?.some(ig => ig.id === selectedPlatform.id));
          
          if (!platformExists) {
            setSelectedPlatform(null);
          }
        }
      }
    } else {
      setAllPlatforms(prev => ({
        ...prev,
        business_pages: [],
        business_groups: [],
        business_instagram: []
      }));
      
      // Clear business platform selection
      if (selectedPlatform && selectedPlatform._sourceType === 'business') {
        setSelectedPlatform(null);
      }
    }
  }, [selectedBusinessManager, user]);

  const loadPosts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/api/posts?user_id=${user._id}`);
      setPosts(response.data.posts);
    } catch (error) {
      console.error('Error loading posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUserPlatforms = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/users/${user._id}/platforms`);
      setAllPlatforms({
        personal_pages: response.data.personal_pages || [],
        personal_groups: response.data.personal_groups || [],
        business_pages: response.data.business_pages || [],
        business_groups: response.data.business_groups || [],
        business_instagram: response.data.business_instagram || []
      });
      
      // Set selected business manager if available
      if (response.data.selected_business_manager) {
        setSelectedBusinessManager(response.data.selected_business_manager);
      }
    } catch (error) {
      console.error('Error loading platforms:', error);
    }
  };

  const handleFacebookLogin = async (accessToken) => {
    try {
      setLoading(true);
      console.log('Authenticating with Meta platforms...', accessToken.substring(0, 20) + '...');
      
      const response = await axios.post(`${API_BASE}/api/auth/facebook`, {
        access_token: accessToken
      });
      
      console.log('Meta auth successful:', response.data);
      setUser(response.data.user);
      
      // Check for business managers
      if (response.data.user.business_managers && response.data.user.business_managers.length > 0) {
        console.log(`Found ${response.data.user.business_managers.length} Business Managers`);
        console.log(`Found ${response.data.total_instagram_accounts} Instagram accounts`);
        
        // Find "Entreprise de Didier Preud'homme" and auto-select it
        const didierBM = response.data.user.business_managers.find(bm => 
          bm.name.toLowerCase().includes("didier") || 
          bm.name.toLowerCase().includes("preud'homme")
        );
        if (didierBM) {
          setSelectedBusinessManager(didierBM);
          console.log('Auto-selected Business Manager:', didierBM.name);
        }
      }
      
      // Set default platform if available
      if (response.data.user.facebook_pages && response.data.user.facebook_pages.length > 0) {
        console.log('Personal pages found:', response.data.user.facebook_pages.length);
      }
      
    } catch (error) {
      console.error('Meta auth error:', error);
      console.error('Error details:', error.response?.data);
      
      let errorMessage = 'Erreur lors de l\'authentification Meta';
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.status === 400) {
        errorMessage = 'Token Facebook invalide ou expiré';
      } else if (error.response?.status >= 500) {
        errorMessage = 'Erreur serveur. Veuillez réessayer.';
      } else if (error.code === 'NETWORK_ERROR' || !error.response) {
        errorMessage = 'Impossible de se connecter au serveur. Vérifiez votre connexion.';
      }
      
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleBusinessManagerSelect = (businessManager) => {
    setSelectedBusinessManager(businessManager);
    setSelectedPlatform(null); // Reset platform selection
    
    if (businessManager && user.business_managers) {
      const bm = user.business_managers.find(b => b.id === businessManager.id);
      if (bm) {
        // Auto-select first available platform (priority: pages > groups > instagram)
        if (bm.pages && bm.pages.length > 0) {
          const firstPage = bm.pages[0];
          firstPage._sourceType = 'business';
          firstPage.platform = 'facebook';
          firstPage.type = 'page';
          setSelectedPlatform(firstPage);
        } else if (bm.groups && bm.groups.length > 0) {
          const firstGroup = bm.groups[0];
          firstGroup._sourceType = 'business';
          firstGroup.platform = 'facebook';
          firstGroup.type = 'group';
          setSelectedPlatform(firstGroup);
        } else if (bm.instagram_accounts && bm.instagram_accounts.length > 0) {
          const firstIG = bm.instagram_accounts[0];
          firstIG._sourceType = 'business';
          firstIG.platform = 'instagram';
          firstIG.type = 'instagram';
          setSelectedPlatform(firstIG);
        }
      }
    }
  };

  const handlePostCreated = (newPost) => {
    setPosts(prev => [newPost, ...prev]);
  };

  const handlePostDeleted = async (postId) => {
    try {
      await axios.delete(`${API_BASE}/api/posts/${postId}`);
      setPosts(prev => prev.filter(post => post.id !== postId));
    } catch (error) {
      console.error('Error deleting post:', error);
      alert('Erreur lors de la suppression du post');
    }
  };

  const handlePostPublished = async (postId) => {
    try {
      setLoading(true);
      await axios.post(`${API_BASE}/api/posts/${postId}/publish`);
      await loadPosts(); // Reload to get updated status
      alert('Post republié avec succès !');
    } catch (error) {
      console.error('Error republishing post:', error);
      alert('Erreur lors de la republication: ' + (error.response?.data?.detail || 'Erreur inconnue'));
    } finally {
      setLoading(false);
    }
  };

  const getPlatformIcon = (platform, type) => {
    if (platform === 'instagram') return <Instagram className="w-4 h-4" />;
    if (type === 'group') return <MessageSquare className="w-4 h-4" />;
    return <Users className="w-4 h-4" />; // Default for pages
  };

  const getPlatformStats = () => {
    const totalPages = allPlatforms.personal_pages.length + allPlatforms.business_pages.length;
    const totalGroups = allPlatforms.personal_groups.length + allPlatforms.business_groups.length;
    const totalInstagram = allPlatforms.business_instagram.length;
    const totalPlatforms = totalPages + totalGroups + totalInstagram;
    
    return { totalPages, totalGroups, totalInstagram, totalPlatforms };
  };

  // Show loading while Facebook SDK initializes
  if (!fbInitialized) {
    return (
      <div className="min-h-screen bg-gray-facebook flex items-center justify-center">
        <div className="facebook-card p-8 max-w-md w-full mx-4 text-center">
          <div className="spinner mx-auto mb-4" />
          <p className="text-gray-600">Chargement du SDK Meta...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-facebook">
        <div className="max-w-4xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <Instagram className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2">Tunnel Instagram Gratuit</h1>
            <p className="text-gray-600 text-lg">Publication automatique sur Instagram @logicamp_berger</p>
          </div>

          {/* Instagram Tunnel Setup Component */}
          <InstagramTunnelSetup 
            user={user}
            onUserConnected={handleFacebookLogin}
            onTunnelReady={(ready) => {
              if (ready) {
                console.log('Tunnel Instagram prêt !');
              }
            }}
          />

          {/* Alternative: Classic Login */}
          <div className="mt-12 max-w-md mx-auto">
            <div className="facebook-card p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">
                Ou connexion classique
              </h3>
              <FacebookLogin onLogin={handleFacebookLogin} loading={loading} />
              
              <div className="mt-4 text-center text-sm text-gray-500">
                <p>✨ Accès complet aux plateformes Meta Business</p>
                <div className="flex justify-center space-x-4 mt-2">
                  <span className="flex items-center space-x-1">
                    <Users className="w-3 h-3" />
                    <span>Pages</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <MessageSquare className="w-3 h-3" />
                    <span>Groupes</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <Instagram className="w-3 h-3" />
                    <span>Instagram</span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const stats = getPlatformStats();

  return (
    <div className="min-h-screen bg-gray-facebook">
      {/* Header */}
      <header className="facebook-card mb-6 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">Meta Publishing Platform</h1>
                <p className="text-sm text-gray-600">Bienvenue, {user.name}</p>
                {selectedBusinessManager && (
                  <p className="text-xs text-blue-600">📊 {selectedBusinessManager.name}</p>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="hidden md:flex items-center space-x-4 text-sm text-gray-600">
                <span className="flex items-center space-x-1">
                  <Users className="w-3 h-3" />
                  <span>{stats.totalPages}</span>
                </span>
                <span className="flex items-center space-x-1">
                  <MessageSquare className="w-3 h-3" />
                  <span>{stats.totalGroups}</span>
                </span>
                <span className="flex items-center space-x-1">
                  <Instagram className="w-3 h-3" />
                  <span>{stats.totalInstagram}</span>
                </span>
              </div>
              
              <PlatformSelector 
                allPlatforms={allPlatforms}
                selectedPlatform={selectedPlatform}
                selectedBusinessManager={selectedBusinessManager}
                onPlatformSelect={setSelectedPlatform}
              />
              
              <button
                onClick={() => {
                  setUser(null);
                  setPosts([]);
                  setSelectedPlatform(null);
                  setSelectedBusinessManager(null);
                  setAllPlatforms({
                    business_pages: [],
                    business_groups: [],
                    business_instagram: [],
                    personal_pages: [],
                    personal_groups: []
                  });
                }}
                className="text-gray-600 hover:text-gray-800 transition-colors"
              >
                Déconnexion
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4">
        {/* Business Manager Selection */}
        {(!selectedBusinessManager || activeTab === 'setup') && (
          <BusinessManagerSelector 
            user={user}
            onBusinessManagerSelect={handleBusinessManagerSelect}
          />
        )}

        {/* Navigation Tabs */}
        <div className="facebook-card mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('setup')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'setup'
                  ? 'text-facebook-primary border-b-2 border-facebook-primary'
                  : 'text-gray-600 hover:text-facebook-primary'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Building2 className="w-4 h-4" />
                <span>Configuration</span>
              </div>
            </button>
            
            <button
              onClick={() => setActiveTab('create')}
              disabled={!selectedBusinessManager}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'create'
                  ? 'text-facebook-primary border-b-2 border-facebook-primary'
                  : selectedBusinessManager 
                    ? 'text-gray-600 hover:text-facebook-primary' 
                    : 'text-gray-400 cursor-not-allowed'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Send className="w-4 h-4" />
                <span>Créer un Post</span>
              </div>
            </button>
            
            <button
              onClick={() => setActiveTab('posts')}
              disabled={!selectedBusinessManager}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'posts'
                  ? 'text-facebook-primary border-b-2 border-facebook-primary'
                  : selectedBusinessManager 
                    ? 'text-gray-600 hover:text-facebook-primary'
                    : 'text-gray-400 cursor-not-allowed'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4" />
                <span>Mes Posts ({posts.length})</span>
              </div>
            </button>
            
            <button
              onClick={() => setActiveTab('webhook')}
              disabled={!selectedBusinessManager}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'webhook'
                  ? 'text-facebook-primary border-b-2 border-facebook-primary'
                  : selectedBusinessManager 
                    ? 'text-gray-600 hover:text-facebook-primary'
                    : 'text-gray-400 cursor-not-allowed'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Package className="w-4 h-4" />
                <span>Historique Webhook</span>
              </div>
            </button>
            
            <button
              onClick={() => setActiveTab('tunnel')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'tunnel'
                  ? 'text-facebook-primary border-b-2 border-facebook-primary'
                  : 'text-gray-600 hover:text-facebook-primary'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Instagram className="w-4 h-4" />
                <span>Tunnel Instagram</span>
              </div>
            </button>
            
            <button
              onClick={() => setActiveTab('guide')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'guide'
                  ? 'text-facebook-primary border-b-2 border-facebook-primary'
                  : 'text-gray-600 hover:text-facebook-primary'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Instagram className="w-4 h-4" />
                <span>Guide Instagram</span>
              </div>
            </button>
            
            <button
              onClick={() => setActiveTab('logicamp')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'logicamp'
                  ? 'text-facebook-primary border-b-2 border-facebook-primary'
                  : 'text-gray-600 hover:text-facebook-primary'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Instagram className="w-4 h-4" />
                <span>@logicamp_berger</span>
              </div>
            </button>
            
            <button
              onClick={() => setActiveTab('multi-platform')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'multi-platform'
                  ? 'text-facebook-primary border-b-2 border-facebook-primary'
                  : 'text-gray-600 hover:text-facebook-primary'
              }`}
            >
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-gradient-to-r from-blue-500 to-pink-500 rounded-full flex items-center justify-center">
                  <Instagram className="w-2 h-2 text-white" />
                </div>
                <span>Connexion Multi-Plateformes</span>
              </div>
            </button>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'setup' && (
          <div className="space-y-6">
            {/* Tunnel Instagram Status Widget */}
            <div className="facebook-card p-6">
              <TunnelStatusWidget user={user} />
            </div>
            
            {/* Connection Status */}
            <div className="facebook-card p-6">
              <ConnectionDiagnostic API_BASE={API_BASE} />
            </div>
            
            {/* Facebook Connection Test */}
            <div className="facebook-card p-6">
              <FacebookConnectionTest API_BASE={API_BASE} />
            </div>
            
            {/* Instagram Diagnostics */}
            <div className="facebook-card p-6">
              <InstagramDiagnostics API_BASE={API_BASE} />
            </div>
            
            {/* Image Orientation Test */}
            <div className="facebook-card p-6">
              <ImageOrientationTest />
            </div>
            
            <div className="facebook-card p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Statut de la configuration Meta</h3>
            
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${user ? 'bg-green-500' : 'bg-red-500'}`} />
                <span>Connexion Meta : {user ? '✅ Connecté' : '❌ Non connecté'}</span>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${
                  user?.business_managers?.length > 0 ? 'bg-green-500' : 'bg-yellow-500'
                }`} />
                <span>Business Managers : {user?.business_managers?.length || 0} trouvé(s)</span>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${selectedBusinessManager ? 'bg-green-500' : 'bg-gray-400'}`} />
                <span>Business Manager sélectionné : {selectedBusinessManager ? selectedBusinessManager.name : 'Aucun'}</span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                {/* Facebook Pages */}
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Users className="w-5 h-5 text-blue-600" />
                    <span className="font-medium text-blue-800">Pages Facebook</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-600">{stats.totalPages}</p>
                  <p className="text-xs text-blue-600">
                    {allPlatforms.personal_pages.length} personnelles + {allPlatforms.business_pages.length} business
                  </p>
                </div>
                
                {/* Facebook Groups */}
                <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <MessageSquare className="w-5 h-5 text-purple-600" />
                    <span className="font-medium text-purple-800">Groupes Facebook</span>
                  </div>
                  <p className="text-2xl font-bold text-purple-600">{stats.totalGroups}</p>
                  <p className="text-xs text-purple-600">
                    {allPlatforms.personal_groups.length} personnels + {allPlatforms.business_groups.length} business
                  </p>
                </div>
                
                {/* Instagram */}
                <div className="p-4 bg-pink-50 border border-pink-200 rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Instagram className="w-5 h-5 text-pink-600" />
                    <span className="font-medium text-pink-800">Instagram Business</span>
                  </div>
                  <p className="text-2xl font-bold text-pink-600">{stats.totalInstagram}</p>
                  <p className="text-xs text-pink-600">
                    Comptes connectés
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 mt-6">
                <div className={`w-3 h-3 rounded-full ${selectedPlatform ? 'bg-green-500' : 'bg-gray-400'}`} />
                <span>Plateforme sélectionnée : {selectedPlatform ? `${selectedPlatform.name} (${selectedPlatform.platform})` : 'Aucune'}</span>
              </div>
            </div>
            
            {selectedBusinessManager && selectedPlatform && (
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-800 font-medium">🎉 Configuration terminée !</p>
                <p className="text-green-700 text-sm mt-1">
                  Vous pouvez maintenant créer et publier des posts sur <strong>{selectedPlatform.name}</strong> 
                  {selectedPlatform.platform === 'instagram' && ' (Instagram)'}
                  {selectedPlatform.type === 'group' && ' (Groupe)'}
                  {selectedPlatform.type === 'page' && ' (Page)'}
                </p>
              </div>
            )}
            
            {stats.totalPlatforms === 0 && selectedBusinessManager && (
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-yellow-800 font-medium">⚠️ Aucune plateforme trouvée</p>
                <p className="text-yellow-700 text-sm mt-1">
                  Vérifiez les permissions et l'accès aux pages/groupes/Instagram dans votre Business Manager.
                </p>
              </div>
            )}
          </div>
          </div>
        )}

        {activeTab === 'create' && selectedBusinessManager && (
          <PostCreator 
            user={user}
            selectedPlatform={selectedPlatform}
            selectedBusinessManager={selectedBusinessManager}
            allPlatforms={allPlatforms}
            onPostCreated={handlePostCreated}
          />
        )}

        {activeTab === 'posts' && selectedBusinessManager && (
          <PostList 
            posts={posts}
            loading={loading}
            onDelete={handlePostDeleted}
            onPublish={handlePostPublished}
            onRefresh={loadPosts}
          />
        )}

        {activeTab === 'webhook' && selectedBusinessManager && (
          <WebhookHistory />
        )}

        {activeTab === 'tunnel' && (
          <InstagramTunnelSetup 
            user={user}
            onUserConnected={handleFacebookLogin}
            onTunnelReady={(ready) => {
              if (ready) {
                console.log('Tunnel Instagram activé !');
              }
            }}
          />
        )}

        {activeTab === 'guide' && (
          <InstagramSetupGuide />
        )}

        {activeTab === 'logicamp' && (
          <LogicampBergerSetup user={user} />
        )}

        {activeTab === 'multi-platform' && (
          <LogicampBergerConnector 
            user={user} 
            onConnectionComplete={(platforms) => {
              console.log('Connexion multi-plateformes établie:', platforms);
              // Optionnellement recharger les données utilisateur ou mettre à jour l'état
              loadUserPlatforms();
            }}
          />
        )}
      </div>
    </div>
  );
}

export default App;