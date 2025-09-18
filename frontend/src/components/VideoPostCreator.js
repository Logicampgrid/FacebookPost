import React, { useState } from 'react';
import { Send, Video, Calendar, Users, Instagram, MessageSquare, Plus, X, Target, Sparkles, Hash, Type, FileText } from 'lucide-react';
import axios from 'axios';
import VideoUploader from './VideoUploader';
import VideoLibrary from './VideoLibrary';
import VideoHistoryWidget from './VideoHistoryWidget';
import { handleAxiosError } from '../utils/errorHandler';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const VideoPostCreator = ({ user, selectedPlatform, selectedBusinessManager, allPlatforms, onPostCreated }) => {
  const [activeTab, setActiveTab] = useState('upload'); // 'upload' or 'library'
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [videoMetadata, setVideoMetadata] = useState({
    title: '',
    description: '',
    hashtags: ''
  });
  const [scheduledTime, setScheduledTime] = useState('');
  const [crossPostMode, setCrossPostMode] = useState(false);
  const [selectedCrossTargets, setSelectedCrossTargets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getPlatformIcon = (platform, type) => {
    if (platform === 'instagram') return <Instagram className="w-4 h-4 text-pink-500" />;
    if (type === 'group') return <MessageSquare className="w-4 h-4 text-purple-500" />;
    return <Users className="w-4 h-4 text-blue-500" />;
  };

  const getAllAvailablePlatforms = () => {
    const platforms = [];
    
    // Business platforms
    if (allPlatforms.business_pages) {
      allPlatforms.business_pages.forEach(page => {
        platforms.push({
          ...page,
          platform: 'facebook',
          type: 'page',
          source: 'business'
        });
      });
    }
    
    if (allPlatforms.business_groups) {
      allPlatforms.business_groups.forEach(group => {
        platforms.push({
          ...group,
          platform: 'facebook',
          type: 'group',
          source: 'business'
        });
      });
    }
    
    if (allPlatforms.business_instagram) {
      allPlatforms.business_instagram.forEach(ig => {
        platforms.push({
          ...ig,
          platform: 'instagram',
          type: 'instagram',
          source: 'business'
        });
      });
    }
    
    return platforms;
  };

  const handleCrossTargetToggle = (platform) => {
    setSelectedCrossTargets(prev => {
      const exists = prev.find(t => t.id === platform.id);
      if (exists) {
        return prev.filter(t => t.id !== platform.id);
      } else {
        return [...prev, {
          id: platform.id,
          name: platform.name || platform.username,
          platform: platform.platform,
          type: platform.type
        }];
      }
    });
  };

  const handleVideoUploaded = (videoData) => {
    setSelectedVideo(videoData);
    setActiveTab('library'); // Switch to library view to show uploaded video
  };

  const handleVideoSelected = (video) => {
    setSelectedVideo(video);
  };

  const handleError = (errorMessage) => {
    setError(errorMessage);
    setTimeout(() => setError(null), 5000);
  };

  const isVideoCompatible = (video, platform) => {
    if (!video || !video.validation) return true;
    
    if (platform === 'instagram') {
      // Instagram: max 60 seconds, max 1GB
      return video.duration <= 60 && video.file_size <= 1024 * 1024 * 1024;
    }
    
    if (platform === 'facebook') {
      // Facebook: max 15 minutes, max 10GB
      return video.duration <= 15 * 60 && video.file_size <= 10 * 1024 * 1024 * 1024;
    }
    
    return true;
  };

  const getIncompatiblePlatforms = () => {
    if (!selectedVideo) return [];
    
    const incompatible = [];
    
    if (crossPostMode) {
      selectedCrossTargets.forEach(target => {
        if (!isVideoCompatible(selectedVideo, target.platform)) {
          incompatible.push(`${target.name} (${target.platform})`);
        }
      });
    } else if (selectedPlatform && !isVideoCompatible(selectedVideo, selectedPlatform.platform)) {
      incompatible.push(`${selectedPlatform.name} (${selectedPlatform.platform})`);
    }
    
    return incompatible;
  };

  const formatHashtags = (hashtags) => {
    if (!hashtags) return '';
    return hashtags
      .split(/[,\s]+/)
      .filter(tag => tag.trim())
      .map(tag => tag.trim().startsWith('#') ? tag.trim() : `#${tag.trim()}`)
      .join(' ');
  };

  const buildVideoPostContent = () => {
    let content = '';
    
    if (videoMetadata.title) {
      content += videoMetadata.title;
    }
    
    if (videoMetadata.description) {
      content += (content ? '\n\n' : '') + videoMetadata.description;
    }
    
    const formattedHashtags = formatHashtags(videoMetadata.hashtags);
    if (formattedHashtags) {
      content += (content ? '\n\n' : '') + formattedHashtags;
    }
    
    return content;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedVideo) {
      setError('Veuillez sélectionner ou uploader une vidéo');
      return;
    }
    
    if (!crossPostMode && !selectedPlatform) {
      setError('Veuillez sélectionner une plateforme');
      return;
    }
    
    if (crossPostMode && selectedCrossTargets.length === 0) {
      setError('Veuillez sélectionner au moins une plateforme pour la publication croisée');
      return;
    }

    const incompatiblePlatforms = getIncompatiblePlatforms();
    if (incompatiblePlatforms.length > 0) {
      if (!window.confirm(
        `Attention: Cette vidéo n'est pas compatible avec:\n${incompatiblePlatforms.join('\n')}\n\nContinuer quand même ?`
      )) {
        return;
      }
    }

    try {
      setLoading(true);
      setError(null);

      const postContent = buildVideoPostContent();

      // Create video post
      const formData = new FormData();
      formData.append('user_id', user._id);
      formData.append('content', postContent);
      formData.append('video_url', selectedVideo.video_url);
      formData.append('video_id', selectedVideo.id);
      
      if (crossPostMode) {
        formData.append('target_type', 'cross-post-video');
        formData.append('target_id', 'cross-post-video');
        formData.append('target_name', `Publication vidéo croisée (${selectedCrossTargets.length} plateformes)`);
        formData.append('platform', 'meta');
        formData.append('cross_post_targets', JSON.stringify(selectedCrossTargets));
      } else {
        formData.append('target_type', selectedPlatform.type);
        formData.append('target_id', selectedPlatform.id);
        formData.append('target_name', selectedPlatform.name || selectedPlatform.username);
        formData.append('platform', selectedPlatform.platform);
      }
      
      if (selectedBusinessManager) {
        formData.append('business_manager_id', selectedBusinessManager.id);
        formData.append('business_manager_name', selectedBusinessManager.name);
      }
      
      if (scheduledTime) {
        formData.append('scheduled_time', scheduledTime);
      }

      // Add video metadata
      formData.append('video_metadata', JSON.stringify({
        title: videoMetadata.title,
        description: videoMetadata.description,
        hashtags: formatHashtags(videoMetadata.hashtags)
      }));

      const response = await axios.post(`${API_BASE}/api/posts/video`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const newPost = response.data.post;

      // Publish immediately if not scheduled
      if (!scheduledTime) {
        try {
          const publishResponse = await axios.post(`${API_BASE}/api/posts/${newPost.id}/publish`);
          console.log('Video post published:', publishResponse.data);
        } catch (publishError) {
          console.error('Error publishing video post:', publishError);
          const errorMessage = handleAxiosError(publishError);
          setError('Post vidéo créé mais échec de publication: ' + errorMessage);
        }
      }

      // Reset form
      setSelectedVideo(null);
      setVideoMetadata({ title: '', description: '', hashtags: '' });
      setScheduledTime('');
      setSelectedCrossTargets([]);
      setCrossPostMode(false);

      // Notify parent
      onPostCreated && onPostCreated(newPost);

      // Show success message
      if (scheduledTime) {
        alert('Post vidéo programmé avec succès !');
      } else {
        alert('Post vidéo publié avec succès ! 🎬');
      }
      
    } catch (error) {
      console.error('Error creating video post:', error);
      const errorMessage = handleAxiosError(error);
      setError('Erreur lors de la création du post vidéo: ' + errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getMinDateTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 5);
    return now.toISOString().slice(0, 16);
  };

  const availablePlatforms = getAllAvailablePlatforms();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="facebook-card p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
            <Video className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-800">Publication de vidéos</h2>
            <p className="text-sm text-gray-600">
              Uploadez et publiez vos vidéos sur Facebook et Instagram
            </p>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Video Selection Tabs */}
        <div className="flex border-b mb-6">
          <button
            onClick={() => setActiveTab('upload')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'upload'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-blue-600'
            }`}
          >
            <Plus className="w-4 h-4 inline mr-1" />
            Uploader une vidéo
          </button>
          <button
            onClick={() => setActiveTab('library')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'library'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-blue-600'
            }`}
          >
            <Video className="w-4 h-4 inline mr-1" />
            Bibliothèque
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'history'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-blue-600'
            }`}
          >
            <Calendar className="w-4 h-4 inline mr-1" />
            Historique
          </button>
        </div>

        {/* Video Upload/Selection */}
        {activeTab === 'upload' && (
          <VideoUploader
            onVideoUploaded={handleVideoUploaded}
            onError={handleError}
            disabled={loading}
          />
        )}

        {activeTab === 'library' && (
          <VideoLibrary
            onVideoSelect={handleVideoSelected}
            onError={handleError}
          />
        )}

        {activeTab === 'history' && (
          <VideoHistoryWidget user={user} />
        )}
      </div>

      {/* Video Post Configuration */}
      {selectedVideo && (
        <div className="facebook-card p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <Send className="w-5 h-5 mr-2" />
            Configuration de la publication
          </h3>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Video Metadata */}
            <div className="space-y-4">
              <h4 className="font-medium text-gray-800 flex items-center">
                <FileText className="w-4 h-4 mr-2" />
                Métadonnées de la vidéo
              </h4>
              
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Type className="w-4 h-4 inline mr-1" />
                  Titre (optionnel)
                </label>
                <input
                  type="text"
                  value={videoMetadata.title}
                  onChange={(e) => setVideoMetadata(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Ex: Découvrez notre nouveau produit !"
                  className="facebook-input w-full"
                  disabled={loading}
                  maxLength={100}
                />
                <div className="mt-1 text-xs text-gray-500">
                  {videoMetadata.title.length}/100 caractères
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={videoMetadata.description}
                  onChange={(e) => setVideoMetadata(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Décrivez votre vidéo..."
                  className="facebook-textarea h-24"
                  disabled={loading}
                  maxLength={1000}
                />
                <div className="mt-1 text-xs text-gray-500">
                  {videoMetadata.description.length}/1000 caractères
                </div>
              </div>

              {/* Hashtags */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Hash className="w-4 h-4 inline mr-1" />
                  Hashtags (séparés par des virgules)
                </label>
                <input
                  type="text"
                  value={videoMetadata.hashtags}
                  onChange={(e) => setVideoMetadata(prev => ({ ...prev, hashtags: e.target.value }))}
                  placeholder="Ex: produit, innovation, qualité"
                  className="facebook-input w-full"
                  disabled={loading}
                />
                <div className="mt-1 text-xs text-gray-500">
                  Seront automatiquement formatés avec #
                </div>
                {videoMetadata.hashtags && (
                  <div className="mt-2 p-2 bg-gray-50 rounded text-sm">
                    <strong>Aperçu:</strong> {formatHashtags(videoMetadata.hashtags)}
                  </div>
                )}
              </div>
            </div>

            {/* Platform Selection */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-gray-800">Plateformes de publication</h4>
                <button
                  type="button"
                  onClick={() => {
                    setCrossPostMode(!crossPostMode);
                    setSelectedCrossTargets([]);
                  }}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    crossPostMode
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {crossPostMode ? 'Mode croisé activé' : 'Activer mode croisé'}
                </button>
              </div>

              {/* Cross-post platform selection */}
              {crossPostMode && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    <Target className="w-4 h-4 inline mr-1" />
                    Sélectionnez les plateformes ({selectedCrossTargets.length} sélectionnée(s))
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-48 overflow-y-auto border border-gray-200 rounded-lg p-3">
                    {availablePlatforms.map((platform) => {
                      const isSelected = selectedCrossTargets.find(t => t.id === platform.id);
                      const isCompatible = isVideoCompatible(selectedVideo, platform.platform);
                      
                      return (
                        <button
                          key={`${platform.source}-${platform.id}`}
                          type="button"
                          onClick={() => isCompatible && handleCrossTargetToggle(platform)}
                          disabled={!isCompatible}
                          className={`p-3 rounded-lg border-2 transition-all text-left ${
                            isSelected 
                              ? 'border-blue-500 bg-blue-50' 
                              : isCompatible
                                ? 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                                : 'border-gray-100 bg-gray-50 opacity-50 cursor-not-allowed'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              {getPlatformIcon(platform.platform, platform.type)}
                              <div className="min-w-0 flex-1">
                                <div className="font-medium text-sm truncate">
                                  {platform.name || platform.username}
                                </div>
                                <div className="text-xs text-gray-500 capitalize">
                                  {platform.platform} {platform.type}
                                </div>
                              </div>
                            </div>
                            {isSelected && (
                              <div className="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                                <div className="w-2 h-2 bg-white rounded-full" />
                              </div>
                            )}
                          </div>
                          {!isCompatible && (
                            <div className="text-xs text-red-500 mt-1">
                              Vidéo non compatible
                            </div>
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Single platform display */}
              {!crossPostMode && selectedPlatform && (
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    {getPlatformIcon(selectedPlatform.platform, selectedPlatform.type)}
                    <span className="text-sm font-medium">
                      {selectedPlatform.name || selectedPlatform.username}
                    </span>
                    <span className="text-xs text-gray-500">
                      ({selectedPlatform.platform})
                    </span>
                    {!isVideoCompatible(selectedVideo, selectedPlatform.platform) && (
                      <span className="text-xs text-red-500 font-medium">
                        ⚠️ Vidéo non compatible
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Schedule Time */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-1" />
                Programmer la publication (optionnel)
              </label>
              <input
                type="datetime-local"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
                min={getMinDateTime()}
                className="facebook-input w-full max-w-xs"
                disabled={loading}
              />
              {scheduledTime && (
                <p className="text-xs text-gray-500 mt-1">
                  Sera publié le {new Date(scheduledTime).toLocaleString('fr-FR')}
                </p>
              )}
            </div>

            {/* Submit Button */}
            <div className="flex justify-between items-center pt-4 border-t">
              <div className="text-sm text-gray-500">
                {selectedVideo ? `Vidéo: ${selectedVideo.filename}` : 'Aucune vidéo sélectionnée'}
              </div>
              
              <button
                type="submit"
                disabled={
                  loading || 
                  !selectedVideo ||
                  (!crossPostMode && !selectedPlatform) ||
                  (crossPostMode && selectedCrossTargets.length === 0)
                }
                className="facebook-button disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <div className="spinner" />
                    <span>Publication...</span>
                  </>
                ) : (
                  <>
                    <Video className="w-4 h-4" />
                    <span>
                      {scheduledTime ? 'Programmer la vidéo' : 
                       crossPostMode ? `Publier sur ${selectedCrossTargets.length} plateformes` :
                       'Publier la vidéo'}
                    </span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Preview */}
      {selectedVideo && videoMetadata && (
        <div className="facebook-card p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Aperçu de la publication
          </h3>
          
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                <Users className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="font-medium text-gray-800">
                  {crossPostMode ? 'Publication multi-plateformes' : (selectedPlatform?.name || 'Ma Page')}
                </div>
                <div className="text-sm text-gray-500">À l'instant</div>
              </div>
            </div>
            
            <div className="space-y-3">
              {buildVideoPostContent() && (
                <div className="text-gray-800 whitespace-pre-line">
                  {buildVideoPostContent()}
                </div>
              )}
              
              <div className="bg-gray-100 rounded-lg p-4 flex items-center space-x-3">
                <Video className="w-8 h-8 text-gray-600" />
                <div>
                  <div className="font-medium text-gray-800">{selectedVideo.filename}</div>
                  <div className="text-sm text-gray-600">
                    Vidéo • {selectedVideo.duration ? `${Math.round(selectedVideo.duration)}s` : 'Durée inconnue'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoPostCreator;