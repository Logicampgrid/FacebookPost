import React, { useState } from 'react';
import { Send, Image, Calendar, Users, Clock, Link } from 'lucide-react';
import axios from 'axios';
import MediaUploader from './MediaUploader';
import PostPreview from './PostPreview';
import LinkPreview from './LinkPreview';
import { useLinkDetection } from '../hooks/useLinkDetection';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const PostCreator = ({ user, selectedPage, selectedBusinessManager, onPostCreated }) => {
  const [content, setContent] = useState('');
  const [mediaFiles, setMediaFiles] = useState([]);
  const [scheduledTime, setScheduledTime] = useState('');
  const [commentLink, setCommentLink] = useState(''); // New state for comment link
  const [loading, setLoading] = useState(false);

  // Hook pour la détection automatique des liens
  const { detectedLinks, loading: linksLoading, removeLink, resetRemovedLinks } = useLinkDetection(content);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!content.trim()) {
      alert('Veuillez saisir un contenu pour votre post');
      return;
    }
    
    if (!selectedPage) {
      alert('Veuillez sélectionner une page Facebook');
      return;
    }

    try {
      setLoading(true);

      // Create post with FormData
      const formData = new FormData();
      formData.append('user_id', user._id);
      formData.append('content', content.trim());
      formData.append('target_type', 'page');
      formData.append('target_id', selectedPage.id);
      formData.append('target_name', selectedPage.name);
      
      // Add Business Manager info if available
      if (selectedBusinessManager) {
        formData.append('business_manager_id', selectedBusinessManager.id);
        formData.append('business_manager_name', selectedBusinessManager.name);
      }
      
      if (scheduledTime) {
        formData.append('scheduled_time', scheduledTime);
      }
      
      // Add comment link if provided
      if (commentLink.trim()) {
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
      }

      // Reset form
      setContent('');
      setMediaFiles([]);
      setScheduledTime('');
      resetRemovedLinks();

      // Notify parent
      onPostCreated(newPost);

      // Show appropriate success message
      if (scheduledTime) {
        alert('Post programmé avec succès!');
      } else {
        alert('Post créé et publié avec succès sur Facebook! 🎉');
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
    now.setMinutes(now.getMinutes() + 5); // Minimum 5 minutes from now
    return now.toISOString().slice(0, 16);
  };

  return (
    <div className="space-y-6">
      {/* Post Creator */}
      <div className="facebook-card p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-facebook-primary rounded-full flex items-center justify-center">
            <Send className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-800">Créer et publier un post</h2>
            <p className="text-sm text-gray-600">
              Publication sur: {selectedPage?.name || 'Sélectionnez une page'}
              {selectedBusinessManager && (
                <span className="block text-xs text-blue-600">
                  📊 Business Manager: {selectedBusinessManager.name}
                </span>
              )}
            </p>
            <p className="text-xs text-green-600 font-medium mt-1">
              ✨ Les posts sont maintenant publiés directement sur Facebook !
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Content Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Contenu du post *
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Que voulez-vous partager?"
              className="facebook-textarea h-32"
              disabled={loading}
            />
            <div className="mt-1 text-xs text-gray-500">
              {content.length}/2000 caractères
            </div>
          </div>

          {/* Media Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Image className="w-4 h-4 inline mr-1" />
              Médias (optionnel)
            </label>
            <MediaUploader 
              files={mediaFiles} 
              onFilesChange={setMediaFiles}
              disabled={loading}
            />
          </div>

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
                  <p>Les images et métadonnées des liens s'afficheront automatiquement sur Facebook</p>
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
              {selectedPage ? (
                <span className="flex items-center">
                  <Users className="w-4 h-4 mr-1" />
                  {selectedPage.name}
                </span>
              ) : (
                'Sélectionnez une page Facebook'
              )}
            </div>
            
            <button
              type="submit"
              disabled={loading || !selectedPage || !content.trim()}
              className="facebook-button disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="spinner" />
                  <span>Création...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>{scheduledTime ? 'Programmer' : 'Publier sur Facebook'}</span>
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
            pageName={selectedPage?.name || 'Ma Page'}
            timestamp="À l'instant"
          />
        </div>
      )}
    </div>
  );
};

export default PostCreator;