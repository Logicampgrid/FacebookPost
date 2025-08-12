import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, Calendar, Send, Building2 } from 'lucide-react';
import PostCreator from './components/PostCreator';
import PostList from './components/PostList';
import FacebookLogin from './components/FacebookLogin';
import PageSelector from './components/PageSelector';
import BusinessManagerSelector from './components/BusinessManagerSelector';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

function App() {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [selectedPage, setSelectedPage] = useState(null);
  const [selectedBusinessManager, setSelectedBusinessManager] = useState(null);
  const [businessPages, setBusinessPages] = useState([]);
  const [personalPages, setPersonalPages] = useState([]);
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
      loadUserPages();
    }
  }, [user]);

  // Update pages when business manager selection changes
  useEffect(() => {
    if (user && selectedBusinessManager) {
      const businessManagerData = user.business_managers?.find(bm => bm.id === selectedBusinessManager.id);
      if (businessManagerData) {
        setBusinessPages(businessManagerData.pages || []);
        // Clear selected page if it's not from the current business manager
        if (selectedPage && selectedPage._sourceType === 'business') {
          const pageExists = businessManagerData.pages?.some(p => p.id === selectedPage.id);
          if (!pageExists) {
            setSelectedPage(null);
          }
        }
      }
    } else {
      setBusinessPages([]);
      // Clear business page selection
      if (selectedPage && selectedPage._sourceType === 'business') {
        setSelectedPage(null);
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

  const loadUserPages = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/users/${user._id}/pages`);
      setPersonalPages(response.data.personal_pages || []);
      setBusinessPages(response.data.business_pages || []);
      
      // Set selected business manager if available
      if (response.data.selected_business_manager) {
        setSelectedBusinessManager(response.data.selected_business_manager);
      }
    } catch (error) {
      console.error('Error loading pages:', error);
    }
  };

  const handleFacebookLogin = async (accessToken) => {
    try {
      setLoading(true);
      console.log('Authenticating with Facebook...', accessToken.substring(0, 20) + '...');
      
      const response = await axios.post(`${API_BASE}/api/auth/facebook`, {
        access_token: accessToken
      });
      
      console.log('Facebook auth successful:', response.data);
      setUser(response.data.user);
      
      // Check for business managers
      if (response.data.user.business_managers && response.data.user.business_managers.length > 0) {
        console.log(`Found ${response.data.user.business_managers.length} Business Managers`);
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
      
      // Set default page if available
      if (response.data.user.facebook_pages && response.data.user.facebook_pages.length > 0) {
        setPersonalPages(response.data.user.facebook_pages);
        console.log('Personal pages found:', response.data.user.facebook_pages.length);
      }
      
    } catch (error) {
      console.error('Facebook auth error:', error);
      console.error('Error details:', error.response?.data);
      
      let errorMessage = 'Erreur lors de l\'authentification Facebook';
      
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
    setSelectedPage(null); // Reset page selection
    
    if (businessManager && user.business_managers) {
      const bm = user.business_managers.find(b => b.id === businessManager.id);
      if (bm && bm.pages && bm.pages.length > 0) {
        // Auto-select first page from business manager
        const firstPage = bm.pages[0];
        firstPage._sourceType = 'business';
        setSelectedPage(firstPage);
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
      alert('Post publié avec succès sur Facebook!');
    } catch (error) {
      console.error('Error publishing post:', error);
      alert('Erreur lors de la publication: ' + (error.response?.data?.detail || 'Erreur inconnue'));
    } finally {
      setLoading(false);
    }
  };

  // Show loading while Facebook SDK initializes
  if (!fbInitialized) {
    return (
      <div className="min-h-screen bg-gray-facebook flex items-center justify-center">
        <div className="facebook-card p-8 max-w-md w-full mx-4 text-center">
          <div className="spinner mx-auto mb-4" />
          <p className="text-gray-600">Chargement de Facebook SDK...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-facebook flex items-center justify-center">
        <div className="facebook-card p-8 max-w-md w-full mx-4">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-facebook-primary rounded-full flex items-center justify-center mx-auto mb-4">
              <Building2 className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Facebook Business Manager</h1>
            <p className="text-gray-600">Connectez-vous pour accéder à vos Business Managers</p>
          </div>
          
          <FacebookLogin onLogin={handleFacebookLogin} loading={loading} />
          
          <div className="mt-6 text-center text-sm text-gray-500">
            <p>Connectez-vous avec Facebook pour accéder à "Entreprise de Didier Preud'homme"</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-facebook">
      {/* Header */}
      <header className="facebook-card mb-6 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-facebook-primary rounded-full flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">Facebook Business Manager</h1>
                <p className="text-sm text-gray-600">Bienvenue, {user.name}</p>
                {selectedBusinessManager && (
                  <p className="text-xs text-blue-600">📊 {selectedBusinessManager.name}</p>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <PageSelector 
                pages={personalPages}
                businessPages={businessPages}
                selectedPage={selectedPage}
                selectedBusinessManager={selectedBusinessManager}
                onPageSelect={setSelectedPage}
              />
              <button
                onClick={() => {
                  setUser(null);
                  setPosts([]);
                  setSelectedPage(null);
                  setSelectedBusinessManager(null);
                  setBusinessPages([]);
                  setPersonalPages([]);
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
          </div>
        </div>

        {/* Content */}
        {activeTab === 'setup' && (
          <div className="facebook-card p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Statut de la configuration</h3>
            
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${user ? 'bg-green-500' : 'bg-red-500'}`} />
                <span>Connexion Facebook : {user ? '✅ Connecté' : '❌ Non connecté'}</span>
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
              
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${businessPages.length > 0 ? 'bg-green-500' : 'bg-gray-400'}`} />
                <span>Pages Business disponibles : {businessPages.length}</span>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${selectedPage ? 'bg-green-500' : 'bg-gray-400'}`} />
                <span>Page sélectionnée : {selectedPage ? selectedPage.name : 'Aucune'}</span>
              </div>
            </div>
            
            {selectedBusinessManager && selectedPage && (
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-800 font-medium">🎉 Configuration terminée !</p>
                <p className="text-green-700 text-sm mt-1">
                  Vous pouvez maintenant créer et publier des posts sur <strong>{selectedPage.name}</strong>
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'create' && selectedBusinessManager && (
          <PostCreator 
            user={user}
            selectedPage={selectedPage}
            selectedBusinessManager={selectedBusinessManager}
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
      </div>
    </div>
  );
}

export default App;