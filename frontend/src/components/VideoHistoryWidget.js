import React, { useState, useEffect } from 'react';
import { Video, Play, Eye, Calendar, Users, Instagram, MessageSquare, Clock, CheckCircle, AlertTriangle, TrendingUp } from 'lucide-react';
import axios from 'axios';
import { handleAxiosError } from '../utils/errorHandler';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const VideoHistoryWidget = ({ user }) => {
  const [videoHistory, setVideoHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    published: 0,
    scheduled: 0,
    failed: 0
  });

  useEffect(() => {
    if (user) {
      loadVideoHistory();
    }
  }, [user]);

  const loadVideoHistory = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/api/posts/video/history?user_id=${user._id}`);
      
      const videos = response.data.videos || [];
      setVideoHistory(videos);
      
      // Calculer les statistiques
      const newStats = {
        total: videos.length,
        published: videos.filter(v => v.status === 'published').length,
        scheduled: videos.filter(v => v.status === 'scheduled').length,
        failed: videos.filter(v => v.status === 'failed').length
      };
      setStats(newStats);
      
    } catch (error) {
      console.error('Error loading video history:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getPlatformIcon = (platform, type) => {
    if (platform === 'instagram') return <Instagram className="w-4 h-4 text-pink-500" />;
    if (type === 'group') return <MessageSquare className="w-4 h-4 text-purple-500" />;
    return <Users className="w-4 h-4 text-blue-500" />;
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'published': { color: 'bg-green-100 text-green-800', icon: CheckCircle, text: 'Publié' },
      'scheduled': { color: 'bg-blue-100 text-blue-800', icon: Clock, text: 'Programmé' },
      'failed': { color: 'bg-red-100 text-red-800', icon: AlertTriangle, text: 'Échec' },
      'draft': { color: 'bg-gray-100 text-gray-800', icon: Clock, text: 'Brouillon' }
    };

    const config = statusConfig[status] || statusConfig['draft'];
    const IconComponent = config.icon;

    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        <IconComponent className="w-3 h-3 mr-1" />
        {config.text}
      </span>
    );
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="facebook-card p-6">
        <div className="flex items-center justify-center">
          <div className="spinner" />
          <span className="ml-2 text-gray-600">Chargement de l'historique...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="facebook-card p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2" />
          Statistiques vidéo
        </h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
            <div className="text-sm text-blue-600">Total</div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{stats.published}</div>
            <div className="text-sm text-green-600">Publiées</div>
          </div>
          
          <div className="bg-yellow-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600">{stats.scheduled}</div>
            <div className="text-sm text-yellow-600">Programmées</div>
          </div>
          
          <div className="bg-red-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
            <div className="text-sm text-red-600">Échecs</div>
          </div>
        </div>
      </div>

      {/* Video History */}
      <div className="facebook-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center">
            <Video className="w-5 h-5 mr-2" />
            Historique des publications vidéo ({videoHistory.length})
          </h3>
          <button
            onClick={loadVideoHistory}
            className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
          >
            Actualiser
          </button>
        </div>

        {videoHistory.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <Video className="w-8 h-8 text-gray-400" />
            </div>
            <h4 className="text-lg font-medium text-gray-800 mb-2">Aucune publication vidéo</h4>
            <p className="text-gray-600">Créez votre première publication vidéo pour voir l'historique ici</p>
          </div>
        ) : (
          <div className="space-y-4">
            {videoHistory.map((video) => (
              <div key={video.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start space-x-4">
                  {/* Video Thumbnail */}
                  <div className="flex-shrink-0">
                    <div className="w-16 h-16 bg-gray-900 rounded-lg flex items-center justify-center">
                      {video.thumbnail_url ? (
                        <img
                          src={video.thumbnail_url}
                          alt="Thumbnail"
                          className="w-full h-full object-cover rounded-lg"
                        />
                      ) : (
                        <Play className="w-6 h-6 text-gray-400" />
                      )}
                    </div>
                  </div>

                  {/* Video Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-800 truncate">
                          {video.video_metadata?.title || video.content?.split('\n')[0] || 'Publication vidéo'}
                        </h4>
                        
                        <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
                          <span className="flex items-center space-x-1">
                            <Calendar className="w-4 h-4" />
                            <span>{formatDate(video.created_at)}</span>
                          </span>
                          
                          {video.duration && (
                            <span className="flex items-center space-x-1">
                              <Clock className="w-4 h-4" />
                              <span>{formatDuration(video.duration)}</span>
                            </span>
                          )}
                        </div>

                        {video.content && (
                          <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                            {video.content}
                          </p>
                        )}
                      </div>

                      <div className="flex-shrink-0 ml-4">
                        {getStatusBadge(video.status)}
                      </div>
                    </div>

                    {/* Platform Info */}
                    <div className="flex items-center justify-between mt-3">
                      <div className="flex items-center space-x-2">
                        {video.cross_post_targets && video.cross_post_targets.length > 0 ? (
                          <div className="flex items-center space-x-1">
                            <span className="text-xs text-gray-500">Publié sur:</span>
                            {video.cross_post_targets.slice(0, 3).map((target, index) => (
                              <div key={index} className="flex items-center space-x-1">
                                {getPlatformIcon(target.platform, target.type)}
                                <span className="text-xs text-gray-600">{target.name}</span>
                              </div>
                            ))}
                            {video.cross_post_targets.length > 3 && (
                              <span className="text-xs text-gray-500">
                                +{video.cross_post_targets.length - 3} autres
                              </span>
                            )}
                          </div>
                        ) : (
                          <div className="flex items-center space-x-1">
                            {getPlatformIcon(video.platform, video.target_type)}
                            <span className="text-xs text-gray-600">{video.target_name}</span>
                          </div>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex items-center space-x-2">
                        {video.video_url && (
                          <button
                            onClick={() => window.open(video.video_url, '_blank')}
                            className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                            title="Voir la vidéo"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        )}
                        
                        {video.platform_post_id && (
                          <button
                            onClick={() => {
                              const platformUrl = video.platform === 'instagram' 
                                ? `https://instagram.com/p/${video.platform_post_id}`
                                : `https://facebook.com/${video.platform_post_id}`;
                              window.open(platformUrl, '_blank');
                            }}
                            className="p-1 text-gray-400 hover:text-green-600 transition-colors"
                            title="Voir sur la plateforme"
                          >
                            <TrendingUp className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Performance Metrics (if available) */}
                    {video.performance && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <div className="grid grid-cols-3 gap-4 text-xs text-gray-600">
                          {video.performance.views && (
                            <div>
                              <span className="font-medium text-gray-800">{video.performance.views}</span>
                              <span className="block">Vues</span>
                            </div>
                          )}
                          {video.performance.likes && (
                            <div>
                              <span className="font-medium text-gray-800">{video.performance.likes}</span>
                              <span className="block">J'aime</span>
                            </div>
                          )}
                          {video.performance.shares && (
                            <div>
                              <span className="font-medium text-gray-800">{video.performance.shares}</span>
                              <span className="block">Partages</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoHistoryWidget;