import React from 'react';
import { MessageCircle, Share2, ThumbsUp } from 'lucide-react';
import LinkPreview from './LinkPreview';

const PostPreview = ({ content, mediaFiles = [], detectedLinks = [], pageName, timestamp, showActions = true }) => {
  const getMediaPreview = (file) => {
    const url = URL.createObjectURL(file);
    
    if (file.type.startsWith('image/')) {
      return (
        <img 
          src={url} 
          alt="Media preview" 
          className="post-media max-h-64"
          onLoad={() => URL.revokeObjectURL(url)}
        />
      );
    } else if (file.type.startsWith('video/')) {
      return (
        <video 
          src={url} 
          controls 
          className="post-media max-h-64"
          onLoad={() => URL.revokeObjectURL(url)}
        />
      );
    }
    
    return null;
  };

  return (
    <div className="post-preview fade-in">
      {/* Post Header */}
      <div className="post-header">
        <div className="w-10 h-10 bg-facebook-primary rounded-full flex items-center justify-center">
          <span className="text-white font-semibold text-sm">
            {pageName.charAt(0).toUpperCase()}
          </span>
        </div>
        <div className="ml-3">
          <h4 className="font-semibold text-gray-800">{pageName}</h4>
          <p className="text-xs text-gray-500">{timestamp}</p>
        </div>
      </div>

      {/* Post Content */}
      {content && (
        <div className="post-content">
          <p className="whitespace-pre-wrap">{content}</p>
        </div>
      )}

      {/* Post Media */}
      {mediaFiles.length > 0 && (
        <div className="space-y-2">
          {mediaFiles.length === 1 ? (
            getMediaPreview(mediaFiles[0])
          ) : (
            <div className={`grid gap-2 ${
              mediaFiles.length === 2 ? 'grid-cols-2' : 
              mediaFiles.length === 3 ? 'grid-cols-2' :
              'grid-cols-2'
            }`}>
              {mediaFiles.slice(0, 4).map((file, index) => (
                <div key={index} className="relative">
                  {getMediaPreview(file)}
                  {index === 3 && mediaFiles.length > 4 && (
                    <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
                      <span className="text-white font-bold text-lg">
                        +{mediaFiles.length - 3}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Post Actions */}
      {showActions && (
        <div className="post-actions">
          <div className="flex items-center space-x-6">
            <button className="flex items-center space-x-1 hover:text-facebook-primary transition-colors">
              <ThumbsUp className="w-4 h-4" />
              <span>J'aime</span>
            </button>
            <button className="flex items-center space-x-1 hover:text-facebook-primary transition-colors">
              <MessageCircle className="w-4 h-4" />
              <span>Commenter</span>
            </button>
            <button className="flex items-center space-x-1 hover:text-facebook-primary transition-colors">
              <Share2 className="w-4 h-4" />
              <span>Partager</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PostPreview;