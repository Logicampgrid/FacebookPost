import React, { useState, useEffect } from 'react';
import { Video, Play, Download, Trash2, Calendar, FileVideo, Eye, Share, Clock, CheckCircle } from 'lucide-react';
import axios from 'axios';
import { handleAxiosError } from '../utils/errorHandler';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const VideoLibrary = ({ onVideoSelect, onError }) => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [deletingVideo, setDeletingVideo] = useState(null);

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/api/videos/library`);
      setVideos(response.data.videos || []);
    } catch (error) {
      console.error('Error loading videos:', error);
      const errorMessage = handleAxiosError(error);
      onError && onError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleVideoSelect = (video) => {
    setSelectedVideo(video);
    onVideoSelect && onVideoSelect(video);
  };

  const handleDeleteVideo = async (videoId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette vidéo ?')) {
      return;
    }

    try {
      setDeletingVideo(videoId);
      await axios.delete(`${API_BASE}/api/videos/${videoId}`);
      setVideos(prev => prev.filter(v => v.id !== videoId));
      
      if (selectedVideo?.id === videoId) {
        setSelectedVideo(null);
      }
    } catch (error) {
      console.error('Error deleting video:', error);
      const errorMessage = handleAxiosError(error);
      onError && onError(errorMessage);
    } finally {
      setDeletingVideo(null);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
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

  const getPlatformBadge = (platforms) => {
    if (!platforms || platforms.length === 0) return null;
    
    return (
      <div className="flex space-x-1">
        {platforms.includes('facebook') && (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
            Facebook
          </span>
        )}
        {platforms.includes('instagram') && (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-pink-100 text-pink-800">
            Instagram
          </span>
        )}
      </div>
    );
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'uploaded': { color: 'bg-green-100 text-green-800', icon: CheckCircle, text: 'Uploadé' },
      'processing': { color: 'bg-yellow-100 text-yellow-800', icon: Clock, text: 'En cours' },
      'published': { color: 'bg-blue-100 text-blue-800', icon: Share, text: 'Publié' },
      'failed': { color: 'bg-red-100 text-red-800', icon: X, text: 'Échec' }
    };

    const config = statusConfig[status] || statusConfig['uploaded'];
    const IconComponent = config.icon;

    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        <IconComponent className="w-3 h-3 mr-1" />
        {config.text}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="spinner" />
        <span className="ml-2 text-gray-600">Chargement de la bibliothèque...</span>
      </div>
    );
  }

  if (videos.length === 0) {
    return (
      <div className="text-center p-8">
        <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <Video className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-800 mb-2">Aucune vidéo</h3>
        <p className="text-gray-600">Uploadez votre première vidéo pour commencer</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center">
          <FileVideo className="w-5 h-5 mr-2" />
          Bibliothèque vidéo ({videos.length})
        </h3>
        <button
          onClick={loadVideos}
          className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
        >
          Actualiser
        </button>
      </div>

      {/* Video Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {videos.map((video) => (
          <div
            key={video.id}
            className={`relative bg-white rounded-lg border-2 transition-all cursor-pointer ${
              selectedVideo?.id === video.id
                ? 'border-blue-500 shadow-lg'
                : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
            }`}
            onClick={() => handleVideoSelect(video)}
          >
            {/* Video Thumbnail */}
            <div className="relative aspect-video bg-gray-900 rounded-t-lg overflow-hidden">
              {video.thumbnail_url ? (
                <img
                  src={video.thumbnail_url}
                  alt={video.filename}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Video className="w-8 h-8 text-gray-400" />
                </div>
              )}
              
              {/* Play Button Overlay */}
              <div className="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                <button className="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors">
                  <Play className="w-6 h-6 text-white" />
                </button>
              </div>
              
              {/* Duration Badge */}
              {video.duration && (
                <div className="absolute bottom-2 right-2 px-2 py-1 bg-black/70 text-white text-xs rounded">
                  {formatDuration(video.duration)}
                </div>
              )}
              
              {/* Status Badge */}
              <div className="absolute top-2 left-2">
                {getStatusBadge(video.status)}
              </div>
            </div>

            {/* Video Info */}
            <div className="p-4 space-y-3">
              <div>
                <h4 className="font-medium text-gray-800 truncate" title={video.filename}>
                  {video.filename}
                </h4>
                <p className="text-sm text-gray-600 mt-1">
                  {formatFileSize(video.file_size)} • {formatDate(video.created_at)}
                </p>
              </div>

              {/* Video Metadata */}
              {video.validation && (
                <div className="text-xs text-gray-500 space-y-1">
                  <div className="flex justify-between">
                    <span>Résolution:</span>
                    <span>{video.validation.width || 'N/A'}x{video.validation.height || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Format:</span>
                    <span>{video.mime_type?.split('/')[1]?.toUpperCase() || 'N/A'}</span>
                  </div>
                </div>
              )}

              {/* Platforms */}
              {video.compatible_platforms && (
                <div>
                  {getPlatformBadge(video.compatible_platforms)}
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-2 border-t border-gray-200">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      window.open(video.video_url, '_blank');
                    }}
                    className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                    title="Voir la vidéo"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      const link = document.createElement('a');
                      link.href = video.video_url;
                      link.download = video.filename;
                      link.click();
                    }}
                    className="p-1 text-gray-400 hover:text-green-600 transition-colors"
                    title="Télécharger"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteVideo(video.id);
                  }}
                  disabled={deletingVideo === video.id}
                  className="p-1 text-gray-400 hover:text-red-600 transition-colors disabled:opacity-50"
                  title="Supprimer"
                >
                  {deletingVideo === video.id ? (
                    <Clock className="w-4 h-4 animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Selection Indicator */}
            {selectedVideo?.id === video.id && (
              <div className="absolute top-2 right-2">
                <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-4 h-4 text-white" />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Selected Video Details */}
      {selectedVideo && (
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-medium text-blue-800 mb-2">Vidéo sélectionnée</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-blue-600">Nom:</span>
              <p className="font-medium text-blue-800 truncate">{selectedVideo.filename}</p>
            </div>
            <div>
              <span className="text-blue-600">Taille:</span>
              <p className="font-medium text-blue-800">{formatFileSize(selectedVideo.file_size)}</p>
            </div>
            <div>
              <span className="text-blue-600">Durée:</span>
              <p className="font-medium text-blue-800">{formatDuration(selectedVideo.duration)}</p>
            </div>
            <div>
              <span className="text-blue-600">Statut:</span>
              <div className="mt-1">{getStatusBadge(selectedVideo.status)}</div>
            </div>
          </div>
          
          {selectedVideo.video_url && (
            <div className="mt-4">
              <a
                href={selectedVideo.video_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
              >
                <Play className="w-4 h-4 mr-1" />
                Voir la vidéo
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoLibrary;