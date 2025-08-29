import React from 'react';
import { ExternalLink, Play } from 'lucide-react';

const MediaDisplay = ({ post, showClickableImages = true, showVideoComments = true }) => {
  const isVideo = post.media_type === 'video' || 
                  (post.image_url && (
                    post.image_url.includes('.mp4') ||
                    post.image_url.includes('.mov') ||
                    post.image_url.includes('.avi') ||
                    post.image_url.includes('.webm') ||
                    post.media_filename?.includes('.mp4') ||
                    post.media_filename?.includes('.mov')
                  ));

  const isImage = !isVideo && (post.image_url || post.media_type === 'image');

  // For videos: display with comment/description
  if (isVideo && post.image_url) {
    return (
      <div className="media-display video-display">
        <div className="relative bg-black rounded-lg overflow-hidden">
          <video
            controls
            className="w-full h-auto max-h-64 object-contain"
            poster={post.image_url?.replace(/\.(mp4|mov|avi|webm)$/i, '_thumb.jpg')}
          >
            <source src={post.image_url} type="video/mp4" />
            Votre navigateur ne supporte pas la lecture vidéo.
          </video>
          
          {/* Video overlay icon */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="bg-black bg-opacity-30 rounded-full p-3">
              <Play className="w-8 h-8 text-white fill-current" />
            </div>
          </div>
        </div>
        
        {/* Video comment/description - Always show for videos */}
        {showVideoComments && post.description && (
          <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-800 mb-1">Commentaire vidéo :</p>
                <p className="text-sm text-blue-700 leading-relaxed">
                  {post.description}
                </p>
                {post.product_url && (
                  <a
                    href={post.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1 text-xs text-blue-600 hover:text-blue-800 mt-2 transition-colors"
                  >
                    <ExternalLink className="w-3 h-3" />
                    <span>Voir le produit</span>
                  </a>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // For images: make them clickable to product URL
  if (isImage && post.image_url) {
    const ImageComponent = (
      <div className="media-display image-display">
        <div className="relative group">
          <img
            src={post.image_url}
            alt={post.title || 'Image produit'}
            className={`w-full h-auto max-h-64 object-contain bg-gray-100 rounded-lg border transition-all duration-200 ${
              showClickableImages && post.product_url 
                ? 'cursor-pointer group-hover:opacity-90 group-hover:scale-[1.02] group-hover:shadow-lg' 
                : ''
            }`}
          />
          
          {/* Clickable overlay for images */}
          {showClickableImages && post.product_url && (
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 rounded-lg flex items-center justify-center">
              <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-white bg-opacity-90 rounded-full p-2">
                <ExternalLink className="w-4 h-4 text-gray-700" />
              </div>
            </div>
          )}
        </div>
        
        {/* Click hint for images */}
        {showClickableImages && post.product_url && (
          <div className="mt-2 text-center">
            <div className="inline-flex items-center space-x-1 text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
              <ExternalLink className="w-3 h-3" />
              <span>Cliquez pour voir le produit</span>
            </div>
          </div>
        )}
      </div>
    );

    // Wrap with clickable link if URL provided
    if (showClickableImages && post.product_url) {
      return (
        <a
          href={post.product_url}
          target="_blank"
          rel="noopener noreferrer"
          className="block"
        >
          {ImageComponent}
        </a>
      );
    }

    return ImageComponent;
  }

  // Fallback for no media
  return (
    <div className="media-display no-media">
      <div className="w-16 h-16 rounded-lg bg-gray-200 flex items-center justify-center">
        <span className="text-gray-400 text-xs">Pas de média</span>
      </div>
    </div>
  );
};

export default MediaDisplay;