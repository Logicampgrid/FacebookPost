import React from 'react';
import { Calendar, Clock, CheckCircle, XCircle, Send, Trash2, RefreshCw } from 'lucide-react';

const PostList = ({ posts, loading, onDelete, onPublish, onRefresh }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'published':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'scheduled':
        return <Clock className="w-4 h-4 text-orange-500" />;
      default:
        return <Calendar className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'published':
        return 'Publié';
      case 'failed':
        return 'Échec';
      case 'scheduled':
        return 'Programmé';
      default:
        return 'Brouillon';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'published':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'scheduled':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="facebook-card p-8 text-center">
        <div className="spinner mx-auto mb-4" />
        <p className="text-gray-600">Chargement des posts...</p>
      </div>
    );
  }

  if (posts.length === 0) {
    return (
      <div className="facebook-card p-8 text-center">
        <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-800 mb-2">Aucun post pour le moment</h3>
        <p className="text-gray-600 mb-6">Commencez par créer votre premier post!</p>
        <button
          onClick={onRefresh}
          className="facebook-button"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Actualiser
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header with refresh */}
      <div className="facebook-card p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-800">
            Mes Posts ({posts.length})
          </h2>
          <button
            onClick={onRefresh}
            className="text-facebook-primary hover:text-facebook-dark transition-colors flex items-center space-x-1"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Actualiser</span>
          </button>
        </div>
      </div>

      {/* Posts List */}
      {posts.map((post) => (
        <div key={post._id} className="facebook-card p-6 fade-in">
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(post.status)} flex items-center space-x-1`}>
                  {getStatusIcon(post.status)}
                  <span>{getStatusText(post.status)}</span>
                </span>
                <span className="text-sm text-gray-500">
                  {post.target_name}
                </span>
              </div>
              <p className="text-sm text-gray-600">
                Créé le {formatDate(post.created_at)}
              </p>
              {post.scheduled_time && (
                <p className="text-sm text-orange-600">
                  Programmé pour le {formatDate(post.scheduled_time)}
                </p>
              )}
              {post.published_at && (
                <p className="text-sm text-green-600">
                  Publié le {formatDate(post.published_at)}
                </p>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              {post.status === 'failed' && (
                <button
                  onClick={() => onPublish(post.id)}
                  className="text-facebook-primary hover:text-facebook-dark transition-colors p-2 rounded-lg hover:bg-facebook-light"
                  title="Republier sur Facebook"
                >
                  <Send className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={() => onDelete(post.id)}
                className="text-red-500 hover:text-red-700 transition-colors p-2 rounded-lg hover:bg-red-50"
                title="Supprimer"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Post Content */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-facebook-primary rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white font-semibold text-xs">
                  {post.target_name.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-800 mb-1">{post.target_name}</h4>
                <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {post.content}
                </p>
                
                {/* Comment Link Info */}
                {post.comment_link && (
                  <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <MessageCircle className="w-4 h-4 text-blue-600" />
                      <span className="text-sm font-medium text-blue-800">Lien en commentaire:</span>
                    </div>
                    <p className="text-sm text-blue-700 mt-1 break-all">{post.comment_link}</p>
                    {post.comment_status && (
                      <div className="mt-2 flex items-center space-x-1">
                        {post.comment_status === 'success' ? (
                          <>
                            <CheckCircle className="w-3 h-3 text-green-500" />
                            <span className="text-xs text-green-600">Commentaire ajouté avec succès</span>
                          </>
                        ) : (
                          <>
                            <XCircle className="w-3 h-3 text-red-500" />
                            <span className="text-xs text-red-600">Échec de l'ajout du commentaire</span>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                )}
                
                {/* Media URLs */}
                {post.media_urls && post.media_urls.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <p className="text-sm font-medium text-gray-600">Médias attachés:</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                      {post.media_urls.map((url, index) => (
                        <div key={index} className="relative">
                          <img 
                            src={process.env.REACT_APP_BACKEND_URL + url} 
                            alt={`Media ${index + 1}`}
                            className="w-full h-16 object-cover rounded border"
                            onError={(e) => {
                              e.target.style.display = 'none';
                            }}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Post Stats/Info */}
          <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between text-sm text-gray-500">
            <div>
              Type: {post.target_type === 'page' ? 'Page Facebook' : 'Groupe Facebook'}
            </div>
            {post.facebook_post_id && (
              <div>
                ID Facebook: {post.facebook_post_id}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default PostList;