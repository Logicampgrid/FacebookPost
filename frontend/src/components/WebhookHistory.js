import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Package, Calendar, ExternalLink, CheckCircle, XCircle, RefreshCw, Store, Users, MessageSquare, Instagram } from 'lucide-react';
import MultiPlatformStatus from './MultiPlatformStatus';
import MediaDisplay from './MediaDisplay';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

const WebhookHistory = () => {
  const [webhookPosts, setWebhookPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [shopMapping, setShopMapping] = useState({});

  useEffect(() => {
    loadWebhookHistory();
  }, []);

  const loadWebhookHistory = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/api/webhook-history?limit=100`);
      setWebhookPosts(response.data.data.webhook_posts || []);
      setShopMapping(response.data.data.shop_mapping || {});
    } catch (error) {
      console.error('Error loading webhook history:', error);
    } finally {
      setLoading(false);
    }
  };

  const getShopIcon = (shopType) => {
    const icons = {
      outdoor: '🏕️',
      gizmobbs: '📱',
      logicantiq: '🏛️'
    };
    return icons[shopType] || '🏪';
  };

  const getShopColor = (shopType) => {
    const colors = {
      outdoor: 'bg-green-100 text-green-800 border-green-200',
      gizmobbs: 'bg-blue-100 text-blue-800 border-blue-200', 
      logicantiq: 'bg-purple-100 text-purple-800 border-purple-200'
    };
    return colors[shopType] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (post) => {
    // Check if this is a comprehensive multi-platform post
    const isMultiPlatform = post.publication_results || post.comprehensive_cross_post;
    const hasPublicationSummary = post.publication_summary;
    
    if (post.status === 'published') {
      if (isMultiPlatform && hasPublicationSummary) {
        const { total_published, total_failed } = post.publication_summary;
        return (
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              <CheckCircle className="w-3 h-3 mr-1" />
              Multi-Plateforme
            </span>
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              ✅ {total_published} | ❌ {total_failed}
            </span>
          </div>
        );
      } else {
        return (
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              <CheckCircle className="w-3 h-3 mr-1" />
              Publié
            </span>
            {post.comment_added && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                💬 Lien ajouté
              </span>
            )}
          </div>
        );
      }
    }
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
        <XCircle className="w-3 h-3 mr-1" />
        Échec
      </span>
    );
  };

  if (loading) {
    return (
      <div className="facebook-card p-6">
        <div className="flex items-center justify-center">
          <div className="spinner mr-3" />
          <span>Chargement de l'historique...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="facebook-card p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Package className="w-6 h-6 text-facebook-primary" />
            <div>
              <h2 className="text-xl font-bold text-gray-800">Historique des Publications Webhook</h2>
              <p className="text-sm text-gray-600">Publications automatiques reçues depuis N8N</p>
            </div>
          </div>
          
          <button
            onClick={loadWebhookHistory}
            disabled={loading}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Actualiser</span>
          </button>
        </div>

        {/* Shop Types Summary */}
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Répartition par boutique :</h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(shopMapping).map(([shopType, config]) => {
              const count = webhookPosts.filter(post => post.shop_type === shopType).length;
              return (
                <div key={shopType} className={`px-3 py-1 rounded-full text-xs font-medium border ${getShopColor(shopType)}`}>
                  {getShopIcon(shopType)} {config.name} ({count})
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Webhook Posts List */}
      <div className="facebook-card">
        {webhookPosts.length === 0 ? (
          <div className="p-8 text-center">
            <Package className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune publication webhook</h3>
            <p className="text-gray-600">
              Les publications automatiques depuis N8N apparaîtront ici.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {webhookPosts.map((post, index) => (
              <div key={post.id || index} className="p-6">
                <div className="flex items-start space-x-4">
                  {/* Media Display - NEW: Videos show comments, Images are clickable */}
                  <div className="flex-shrink-0">
                    <MediaDisplay 
                      post={post} 
                      showClickableImages={true} 
                      showVideoComments={true} 
                    />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-gray-900 truncate">
                          {post.title}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                          {post.description}
                        </p>
                      </div>
                      
                      <div className="flex-shrink-0 ml-4">
                        {getStatusBadge(post)}
                      </div>
                    </div>

                    {/* Meta Information */}
                    <div className="mt-3 flex flex-wrap items-center gap-4 text-sm text-gray-500">
                      {/* Shop Type */}
                      <div className="flex items-center space-x-1">
                        <Store className="w-4 h-4" />
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${getShopColor(post.shop_type)}`}>
                          {getShopIcon(post.shop_type)} {shopMapping[post.shop_type]?.name || post.shop_type}
                        </span>
                      </div>

                      {/* Page */}
                      <div className="flex items-center space-x-1">
                        <span>📄</span>
                        <span>{post.page_name}</span>
                      </div>

                      {/* Date */}
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-4 h-4" />
                        <span>{formatDate(post.received_at)}</span>
                      </div>

                      {/* Product Link */}
                      {post.product_url && (
                        <a
                          href={post.product_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-1 text-facebook-primary hover:text-facebook-secondary transition-colors"
                        >
                          <ExternalLink className="w-4 h-4" />
                          <span>Voir le produit</span>
                        </a>
                      )}

                      {/* Facebook Post Link */}
                      {post.facebook_post_id && (
                        <a
                          href={`https://facebook.com/${post.facebook_post_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-1 text-blue-600 hover:text-blue-700 transition-colors"
                        >
                          <span>📘</span>
                          <span>Voir sur Facebook</span>
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Usage Information - Updated for multipart/form-data */}
      <div className="facebook-card p-6 bg-blue-50 border-blue-200">
        <h3 className="text-lg font-medium text-blue-900 mb-3">Configuration N8N - Format Multipart</h3>
        <div className="space-y-4">
          <div>
            <h4 className="font-medium text-blue-900 mb-2">Endpoint Webhook :</h4>
            <code className="bg-blue-100 px-2 py-1 rounded text-sm text-blue-900">
              POST https://social-media-fixer.preview.emergentagent.com/api/webhook
            </code>
          </div>
          
          <div>
            <h4 className="font-medium text-blue-900 mb-2">Format HTTP Request (multipart/form-data) :</h4>
            <div className="bg-blue-100 rounded-lg p-3 text-sm">
              <div className="space-y-2">
                <div>
                  <span className="font-medium text-blue-900">Content-Type:</span> 
                  <code className="ml-2 text-blue-800">multipart/form-data</code>
                </div>
                <div>
                  <span className="font-medium text-blue-900">Champ json_data (string):</span>
                  <pre className="mt-1 text-blue-900 text-xs">
{`{
  "store": "gizmobbs",
  "title": "Titre de l'item",
  "url": "URL du produit ou de la boutique",
  "description": "Commentaire ou description"
}`}
                  </pre>
                </div>
                <div className="pt-2 border-t border-blue-200">
                  <span className="font-medium text-blue-900">Champ binaire :</span>
                  <div className="ml-4 mt-1 text-blue-800 text-sm">
                    <div>• <code>image</code> : fichier image (jpg, png, webp)</div>
                    <div>• <code>video</code> : fichier vidéo (mp4, mov, avi, webm)</div>
                    <div className="text-xs text-blue-600 mt-1">⚠️ Un seul type par requête</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-green-100 border border-green-200 rounded-lg p-3">
            <h4 className="font-medium text-green-900 mb-2">✨ Comportements automatiques :</h4>
            <div className="text-sm text-green-800 space-y-1">
              <div>🎥 <strong>Vidéos</strong> : Le commentaire s'affiche automatiquement</div>
              <div>🖼️ <strong>Images</strong> : Cliquables vers l'URL du produit</div>
              <div>🏪 <strong>Store</strong> : "gizmobbs" = publication sur votre boutique</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WebhookHistory;