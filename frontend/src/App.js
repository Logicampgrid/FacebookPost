import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, Calendar, Image, Video, Link, Send, Trash2, Clock, CheckCircle, XCircle } from 'lucide-react';
import PostCreator from './components/PostCreator';
import PostList from './components/PostList';
import FacebookLogin from './components/FacebookLogin';
import PageSelector from './components/PageSelector';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [selectedPage, setSelectedPage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('create');

  // Initialize Facebook SDK
  useEffect(() => {
    window.fbAsyncInit = function() {
      window.FB.init({
        appId: '5664227323683118',
        cookie: true,
        xfbml: true,
        version: 'v18.0'
      });
    };
  }, []);

  // Load posts when user is authenticated
  useEffect(() => {
    if (user) {
      loadPosts();
    }
  }, [user]);

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

  const handleFacebookLogin = async (accessToken) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE}/api/auth/facebook`, {
        access_token: accessToken
      });
      
      setUser(response.data.user);
      
      // Set default page if available
      if (response.data.user.facebook_pages && response.data.user.facebook_pages.length > 0) {
        setSelectedPage(response.data.user.facebook_pages[0]);
      }
    } catch (error) {
      console.error('Facebook auth error:', error);
      alert('Erreur lors de l\'authentification Facebook');
    } finally {
      setLoading(false);
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

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-facebook flex items-center justify-center">
        <div className="facebook-card p-8 max-w-md w-full mx-4">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-facebook-primary rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Facebook Post Manager</h1>
            <p className="text-gray-600">Créez et publiez vos posts avec un design moderne</p>
          </div>
          
          <FacebookLogin onLogin={handleFacebookLogin} loading={loading} />
          
          <div className="mt-6 text-center text-sm text-gray-500">
            <p>Connectez-vous avec Facebook pour commencer à créer vos posts</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-facebook">
      {/* Header */}
      <header className="facebook-card mb-6 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-facebook-primary rounded-full flex items-center justify-center">
                <Users className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">Facebook Post Manager</h1>
                <p className="text-sm text-gray-600">Bienvenue, {user.name}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <PageSelector 
                pages={user.facebook_pages} 
                selectedPage={selectedPage}
                onPageSelect={setSelectedPage}
              />
              <button
                onClick={() => {
                  setUser(null);
                  setPosts([]);
                  setSelectedPage(null);
                }}
                className="text-gray-600 hover:text-gray-800 transition-colors"
              >
                Déconnexion
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4">
        {/* Navigation Tabs */}
        <div className="facebook-card mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('create')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'create'
                  ? 'text-facebook-primary border-b-2 border-facebook-primary'
                  : 'text-gray-600 hover:text-facebook-primary'
              }`}
            >
              <div className="flex items-center space-x-2">
                <Send className="w-4 h-4" />
                <span>Créer un Post</span>
              </div>
            </button>
            
            <button
              onClick={() => setActiveTab('posts')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'posts'
                  ? 'text-facebook-primary border-b-2 border-facebook-primary'
                  : 'text-gray-600 hover:text-facebook-primary'
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
        {activeTab === 'create' ? (
          <PostCreator 
            user={user}
            selectedPage={selectedPage}
            onPostCreated={handlePostCreated}
          />
        ) : (
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