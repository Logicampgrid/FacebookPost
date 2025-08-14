import React, { useState } from 'react';
import { Send, Image, Calendar, Users, Clock, Link, Instagram, MessageSquare, Plus, X, Target } from 'lucide-react';
import axios from 'axios';
import MediaUploader from './MediaUploader';
import PostPreview from './PostPreview';
import LinkPreview from './LinkPreview';
import { useLinkDetection } from '../hooks/useLinkDetection';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const PostCreator = ({ user, selectedPlatform, selectedBusinessManager, allPlatforms, onPostCreated }) => {
  const [content, setContent] = useState('');
  const [mediaFiles, setMediaFiles] = useState([]);
  const [scheduledTime, setScheduledTime] = useState('');
  const [commentLink, setCommentLink] = useState('');
  const [commentText, setCommentText] = useState('');  // New state for comment text
  const [crossPostMode, setCrossPostMode] = useState(false);
  const [selectedCrossTargets, setSelectedCrossTargets] = useState([]);
  const [loading, setLoading] = useState(false);

  // Hook pour la détection automatique des liens
  const { detectedLinks, loading: linksLoading, removeLink, resetRemovedLinks } = useLinkDetection(content);

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
    
    // Personal platforms
    if (allPlatforms.personal_pages) {
      allPlatforms.personal_pages.forEach(page => {
        platforms.push({
          ...page,
          platform: 'facebook',
          type: 'page',
          source: 'personal'
        });
      });
    }
    
    if (allPlatforms.personal_groups) {
      allPlatforms.personal_groups.forEach(group => {
        platforms.push({
          ...group,
          platform: 'facebook',
          type: 'group',
          source: 'personal'
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

  const isInstagramCompatible = () => {
    // Instagram requires media: either uploaded files OR links with images
    if (mediaFiles.length > 0) {
      return true; // Uploaded media has priority
    }
    
    // Check if any detected links have images
    if (detectedLinks.length > 0 && detectedLinks.some(link => link.image)) {
      return true;
    }
    
    return false;
  };

  const getIncompatibleWarnings = () => {
    const warnings = [];
    
    if (crossPostMode) {
      const instagramTargets = selectedCrossTargets.filter(t => t.platform === 'instagram');
      if (instagramTargets.length > 0 && !isInstagramCompatible()) {
        warnings.push('Instagram nécessite au moins une image ou un lien avec image');
      }
    } else if (selectedPlatform?.platform === 'instagram' && !isInstagramCompatible()) {
      warnings.push('Instagram nécessite au moins une image ou un lien avec image');
    }
    
    return warnings;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Allow empty content if there are media files
    if (!content.trim() && mediaFiles.length === 0) {
      alert('Veuillez saisir un contenu ou ajouter des médias pour votre post');
      return;
    }
    
    if (!crossPostMode && !selectedPlatform) {
      alert('Veuillez sélectionner une plateforme');
      return;
    }
    
    if (crossPostMode && selectedCrossTargets.length === 0) {
      alert('Veuillez sélectionner au moins une plateforme pour la publication croisée');
      return;
    }

    const warnings = getIncompatibleWarnings();
    if (warnings.length > 0) {
      if (!window.confirm(`Attention :\n${warnings.join('\n')}\n\nContinuer quand même ?`)) {
        return;
      }
    }

    try {
      setLoading(true);

      // Create post with FormData
      const formData = new FormData();
      formData.append('user_id', user._id);
      formData.append('content', content.trim());
      
      if (crossPostMode) {
        // Cross-posting mode
        formData.append('target_type', 'cross-post');
        formData.append('target_id', 'cross-post');
        formData.append('target_name', `Cross-post (${selectedCrossTargets.length} plateformes)`);
        formData.append('platform', 'meta');
        formData.append('cross_post_targets', JSON.stringify(selectedCrossTargets));
      } else {
        // Single platform mode
        formData.append('target_type', selectedPlatform.type);
        formData.append('target_id', selectedPlatform.id);
        formData.append('target_name', selectedPlatform.name || selectedPlatform.username);
        formData.append('platform', selectedPlatform.platform);
      }
      
      // Add Business Manager info if available
      if (selectedBusinessManager) {
        formData.append('business_manager_id', selectedBusinessManager.id);
        formData.append('business_manager_name', selectedBusinessManager.name);
      }
      
      if (scheduledTime) {
        formData.append('scheduled_time', scheduledTime);
      }
      
      // Add comment text if provided (Facebook only)
      if (commentText.trim() && (
        !crossPostMode && selectedPlatform.platform === 'facebook' ||
        crossPostMode && selectedCrossTargets.some(t => t.platform === 'facebook')
      )) {
        formData.append('comment_text', commentText.trim());
      }
      
      // Add comment link if provided (Facebook only) - for backward compatibility
      if (commentLink.trim() && (
        !crossPostMode && selectedPlatform.platform === 'facebook' ||
        crossPostMode && selectedCrossTargets.some(t => t.platform === 'facebook')
      )) {
        formData.append('comment_link', commentLink.trim());
      }

      const response = await axios.post(`${API_BASE}/api/posts`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      const newPost = response.data.post;

      // Upload media if present
      if (mediaFiles.length > 0) {
        for (const file of mediaFiles) {
          const mediaFormData = new FormData();
          mediaFormData.append('file', file);
          
          await axios.post(`${API_BASE}/api/posts/${newPost.id}/media`, mediaFormData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
        }
        
        // Publish the post after media upload (if not scheduled)
        if (!scheduledTime) {
          try {
            const publishResponse = await axios.post(`${API_BASE}/api/posts/${newPost.id}/publish`);
            console.log('Post published after media upload:', publishResponse.data);
          } catch (publishError) {
            console.error('Error publishing post after media upload:', publishError);
            alert('Post créé avec médias mais échec de publication: ' + (publishError.response?.data?.detail || 'Erreur inconnue'));
          }
        }
      } else if (!scheduledTime) {
        // No media files, publish immediately
        try {
          const publishResponse = await axios.post(`${API_BASE}/api/posts/${newPost.id}/publish`);
          console.log('Post published immediately:', publishResponse.data);
        } catch (publishError) {
          console.error('Error publishing post:', publishError);
          alert('Post créé mais échec de publication: ' + (publishError.response?.data?.detail || 'Erreur inconnue'));
        }
      }

      // Reset form
      setContent('');
      setMediaFiles([]);
      setScheduledTime('');
      setCommentLink('');
      setCommentText('');  // Reset comment text
      setSelectedCrossTargets([]);
      setCrossPostMode(false);
      resetRemovedLinks();

      // Notify parent
      onPostCreated(newPost);

      // Show appropriate success message
      if (scheduledTime) {
        alert('Post programmé avec succès !');
      } else {
        const successMessage = response.data.message || 'Post créé et publié avec succès ! 🎉';
        alert(successMessage);
      }
      
    } catch (error) {
      console.error('Error creating post:', error);
      alert('Erreur lors de la création du post: ' + (error.response?.data?.detail || 'Erreur inconnue'));
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
      {/* Post Creator */}
      <div className="facebook-card p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <Send className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-800">Créer et publier sur Meta</h2>
            <p className="text-sm text-gray-600">
              {crossPostMode ? (
                `Publication croisée sur ${selectedCrossTargets.length} plateforme(s)`
              ) : (
                selectedPlatform ? 
                  `Publication sur: ${selectedPlatform.name || selectedPlatform.username} (${selectedPlatform.platform})` :
                  'Sélectionnez une plateforme'
              )}
              {selectedBusinessManager && (
                <span className="block text-xs text-blue-600">
                  📊 Business Manager: {selectedBusinessManager.name}
                </span>
              )}
            </p>
          </div>
        </div>

        {/* Cross-post Toggle */}
        <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-800 flex items-center">
                <Target className="w-4 h-4 mr-2" />
                Mode de publication
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                {crossPostMode ? 
                  'Publiez simultanément sur plusieurs plateformes Meta' : 
                  'Publiez sur une seule plateforme'
                }
              </p>
            </div>
            <button
              type="button"
              onClick={() => {
                setCrossPostMode(!crossPostMode);
                setSelectedCrossTargets([]);
              }}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                crossPostMode 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              {crossPostMode ? 'Mode Simple' : 'Publication Croisée'}
            </button>
          </div>
        </div>

        {/* Cross-post platform selection */}
        {crossPostMode && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              <Target className="w-4 h-4 inline mr-1" />
              Sélectionnez les plateformes ({selectedCrossTargets.length} sélectionnée(s))
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-48 overflow-y-auto border border-gray-200 rounded-lg p-3">
              {availablePlatforms.map((platform) => {
                const isSelected = selectedCrossTargets.find(t => t.id === platform.id);
                const isInstagram = platform.platform === 'instagram';
                const isCompatible = !isInstagram || isInstagramCompatible();
                
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
                        Nécessite une image
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
            {selectedCrossTargets.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {selectedCrossTargets.map((target) => (
                  <span
                    key={target.id}
                    className="inline-flex items-center px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                  >
                    {getPlatformIcon(target.platform, target.type)}
                    <span className="ml-1">{target.name}</span>
                    <button
                      type="button"
                      onClick={() => handleCrossTargetToggle(target)}
                      className="ml-1 hover:text-blue-600"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Content Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Contenu du post (optionnel si vous ajoutez des médias)
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Que voulez-vous partager sur les plateformes Meta ? (Optionnel si vous ajoutez des images)"
              className="facebook-textarea h-32"
              disabled={loading}
            />
            <div className="mt-1 text-xs text-gray-500">
              {content.length}/2000 caractères
            </div>
          </div>

          {/* Compatibility warnings */}
          {getIncompatibleWarnings().length > 0 && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <Instagram className="w-4 h-4 text-yellow-600" />
                <span className="text-sm font-medium text-yellow-800">Attention Instagram</span>
              </div>
              {getIncompatibleWarnings().map((warning, index) => (
                <p key={index} className="text-sm text-yellow-700 mt-1">⚠️ {warning}</p>
              ))}
            </div>
          )}

          {/* Media Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Image className="w-4 h-4 inline mr-1" />
              Médias (prioritaire sur les images des liens)
            </label>
            <MediaUploader 
              files={mediaFiles} 
              onFilesChange={setMediaFiles}
              disabled={loading}
            />
            {mediaFiles.length > 0 && detectedLinks.some(link => link.image) && (
              <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700">
                <span className="font-medium">📸 Priorité :</span> Vos images uploadées seront utilisées à la place des images des liens détectés
              </div>
            )}
            
            {/* Clickable Images Indicator */}
            {mediaFiles.length > 0 && (detectedLinks.length > 0 || commentLink) && (
              (!crossPostMode && selectedPlatform?.platform === 'facebook') || 
              (crossPostMode && selectedCrossTargets.some(t => t.platform === 'facebook'))
            ) && (
              <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Target className="w-4 h-4 text-green-600" />
                  <span className="text-sm font-medium text-green-800">Images cliquables activées</span>
                </div>
                <p className="text-xs text-green-700 mt-1">
                  🎯 <strong>Nouveau :</strong> Vos images seront cliquables sur Facebook et redirigeront vers{' '}
                  {detectedLinks.length > 0 ? 
                    `le lien détecté (${detectedLinks[0].url.substring(0, 30)}...)` : 
                    'le lien du commentaire'
                  } comme un partage Facebook !
                </p>
              </div>
            )}
          </div>

          {/* Comment Section - Facebook only */}
          {((!crossPostMode && selectedPlatform?.platform === 'facebook') || 
            (crossPostMode && selectedCrossTargets.some(t => t.platform === 'facebook'))) && (
            <div className="space-y-4">
              <div className="border-t pt-4">
                <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Commentaire automatique (Facebook uniquement)
                </h3>
                <p className="text-xs text-gray-500 mb-4">
                  💡 <strong>Stratégie :</strong> Ajoutez automatiquement un commentaire après la publication pour maximiser l'engagement et la portée organique sur Facebook
                </p>
                
                {/* Comment Text */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Texte du commentaire
                  </label>
                  <textarea
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    placeholder="Écrivez votre commentaire ici... (question, call-to-action, information supplémentaire)"
                    className="facebook-textarea h-20 text-sm"
                    disabled={loading}
                  />
                  <div className="mt-1 text-xs text-gray-500">
                    {commentText.length}/500 caractères
                  </div>
                </div>
                
                {/* Comment Link - Legacy support */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Link className="w-4 h-4 inline mr-1" />
                    Ou un lien en commentaire
                  </label>
                  <input
                    type="url"
                    value={commentLink}
                    onChange={(e) => setCommentLink(e.target.value)}
                    placeholder="https://exemple.com - Sera ajouté en commentaire si aucun texte ci-dessus"
                    className="facebook-input w-full text-sm"
                    disabled={loading}
                  />
                </div>
                
                {(commentText || commentLink) && (
                  <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-800 font-medium mb-1">📝 Aperçu du commentaire :</p>
                    <div className="text-sm text-blue-700 bg-white p-2 rounded border">
                      {commentText || commentLink}
                    </div>
                    <p className="text-xs text-blue-600 mt-2">
                      ✨ Ce commentaire sera automatiquement ajouté après la publication sur Facebook
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Detected Links Preview */}
          {(detectedLinks.length > 0 || linksLoading) && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Link className="w-4 h-4 inline mr-1" />
                Liens détectés
                {linksLoading && (
                  <span className="ml-2 text-xs text-gray-500">
                    (Chargement...)
                  </span>
                )}
              </label>
              
              <div className="space-y-2">
                {linksLoading && detectedLinks.length === 0 && (
                  <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                    <div className="animate-pulse">
                      <div className="h-3 bg-gray-300 rounded mb-2"></div>
                      <div className="h-2 bg-gray-300 rounded w-3/4"></div>
                    </div>
                  </div>
                )}
                
                {detectedLinks.map((link, index) => (
                  <LinkPreview 
                    key={`${link.url}-${index}`}
                    link={link}
                    onRemove={removeLink}
                  />
                ))}
              </div>
              
              {detectedLinks.length > 0 && (
                <div className="text-xs text-gray-500 mt-1">
                  <p className="text-green-600 font-medium">✓ {detectedLinks.length} lien(s) détecté(s) avec prévisualisation</p>
                  <p>Les images et métadonnées s'afficheront automatiquement sur toutes les plateformes</p>
                </div>
              )}
            </div>
          )}

          {/* Schedule Time */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Clock className="w-4 h-4 inline mr-1" />
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
              {crossPostMode ? (
                selectedCrossTargets.length > 0 ? (
                  <span className="flex items-center">
                    <Target className="w-4 h-4 mr-1" />
                    {selectedCrossTargets.length} plateforme(s) sélectionnée(s)
                  </span>
                ) : (
                  'Sélectionnez des plateformes'
                )
              ) : (
                selectedPlatform ? (
                  <span className="flex items-center">
                    {getPlatformIcon(selectedPlatform.platform, selectedPlatform.type)}
                    <span className="ml-1">{selectedPlatform.name || selectedPlatform.username}</span>
                  </span>
                ) : (
                  'Sélectionnez une plateforme'
                )
              )}
            </div>
            
            <button
              type="submit"
              disabled={
                loading || 
                (!content.trim() && mediaFiles.length === 0) || 
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
                  <Send className="w-4 h-4" />
                  <span>
                    {scheduledTime ? 'Programmer' : 
                     crossPostMode ? `Publier sur ${selectedCrossTargets.length} plateformes` :
                     'Publier'}
                  </span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Live Preview */}
      {(content || mediaFiles.length > 0) && (
        <div className="facebook-card p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <Calendar className="w-5 h-5 mr-2" />
            Aperçu du post
          </h3>
          <PostPreview 
            content={content}
            mediaFiles={mediaFiles}
            detectedLinks={detectedLinks}
            pageName={crossPostMode ? 'Multi-plateforme' : (selectedPlatform?.name || selectedPlatform?.username || 'Ma Page')}
            timestamp="À l'instant"
            platform={crossPostMode ? 'meta' : selectedPlatform?.platform}
          />
          
          {crossPostMode && selectedCrossTargets.length > 0 && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium text-gray-700 mb-2">Publication sur :</p>
              <div className="flex flex-wrap gap-2">
                {selectedCrossTargets.map((target) => (
                  <span
                    key={target.id}
                    className="inline-flex items-center px-2 py-1 bg-white border border-gray-200 text-xs rounded"
                  >
                    {getPlatformIcon(target.platform, target.type)}
                    <span className="ml-1">{target.name}</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PostCreator;