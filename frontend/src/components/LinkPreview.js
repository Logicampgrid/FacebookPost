import React from 'react';
import { ExternalLink } from 'lucide-react';

const LinkPreview = ({ link, onRemove = null }) => {
  const handleClick = () => {
    window.open(link.url, '_blank', 'noopener,noreferrer');
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    if (onRemove) {
      onRemove(link.url);
    }
  };

  return (
    <div 
      onClick={handleClick}
      className="link-preview border border-gray-200 rounded-lg overflow-hidden hover:border-facebook-primary transition-colors cursor-pointer bg-white"
    >
      {/* Link Image */}
      {link.image && (
        <div className="aspect-video bg-gray-100 overflow-hidden">
          <img 
            src={link.image} 
            alt={link.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
        </div>
      )}
      
      {/* Link Content */}
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            {/* Site Name */}
            {link.site_name && (
              <div className="flex items-center text-xs text-gray-500 mb-1">
                <ExternalLink className="w-3 h-3 mr-1" />
                <span className="truncate">{link.site_name}</span>
              </div>
            )}
            
            {/* Title */}
            {link.title && (
              <h3 className="font-semibold text-gray-900 text-sm line-clamp-2 mb-1">
                {link.title}
              </h3>
            )}
            
            {/* Description */}
            {link.description && (
              <p className="text-xs text-gray-600 line-clamp-2">
                {link.description}
              </p>
            )}
            
            {/* URL */}
            <div className="text-xs text-facebook-primary mt-2 truncate">
              {link.url}
            </div>
          </div>
          
          {/* Remove Button */}
          {onRemove && (
            <button
              onClick={handleRemove}
              className="ml-2 text-gray-400 hover:text-red-500 transition-colors p-1"
              title="Supprimer l'aperçu"
            >
              ×
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default LinkPreview;