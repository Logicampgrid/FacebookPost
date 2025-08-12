import React, { useState } from 'react';
import { ChevronDown, Users, MessageSquare, Instagram, Building2 } from 'lucide-react';

const PlatformSelector = ({ 
  allPlatforms, 
  selectedPlatform, 
  selectedBusinessManager,
  onPlatformSelect 
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const getPlatformIcon = (platform, type) => {
    if (platform === 'instagram') return <Instagram className="w-4 h-4 text-pink-500" />;
    if (type === 'group') return <MessageSquare className="w-4 h-4 text-purple-500" />;
    return <Users className="w-4 h-4 text-blue-500" />; // Default for pages
  };

  const getPlatformBadge = (platform, type) => {
    if (platform === 'instagram') return 'IG';
    if (type === 'group') return 'GRP';
    return 'PAGE';
  };

  const getBadgeColor = (platform, type) => {
    if (platform === 'instagram') return 'bg-pink-100 text-pink-800';
    if (type === 'group') return 'bg-purple-100 text-purple-800';
    return 'bg-blue-100 text-blue-800';
  };

  const handlePlatformSelect = (platform, source) => {
    platform._sourceType = source;
    onPlatformSelect(platform);
    setIsOpen(false);
  };

  const renderPlatformGroup = (platforms, title, source, emptyMessage) => {
    if (!platforms || platforms.length === 0) {
      return (
        <div className="p-3 text-gray-500 text-sm italic">
          {emptyMessage}
        </div>
      );
    }

    return (
      <div>
        <div className="px-3 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50">
          {title}
        </div>
        {platforms.map((platform) => (
          <button
            key={`${source}-${platform.id}`}
            onClick={() => handlePlatformSelect(platform, source)}
            className="w-full px-3 py-2 text-left hover:bg-gray-100 flex items-center justify-between group"
          >
            <div className="flex items-center space-x-3">
              {getPlatformIcon(platform.platform, platform.type)}
              <div>
                <div className="font-medium text-gray-900">{platform.name || platform.username}</div>
                <div className="text-xs text-gray-500">
                  {platform.category || platform.privacy || 'Business Account'}
                  {platform.followers_count && ` • ${platform.followers_count} followers`}
                </div>
              </div>
            </div>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getBadgeColor(platform.platform, platform.type)}`}>
              {getPlatformBadge(platform.platform, platform.type)}
            </span>
          </button>
        ))}
      </div>
    );
  };

  const getTotalPlatforms = () => {
    const businessPlatforms = [
      ...(allPlatforms.business_pages || []),
      ...(allPlatforms.business_groups || []),
      ...(allPlatforms.business_instagram || [])
    ];
    const personalPlatforms = [
      ...(allPlatforms.personal_pages || []),
      ...(allPlatforms.personal_groups || [])
    ];
    return businessPlatforms.length + personalPlatforms.length;
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="facebook-button flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
      >
        {selectedPlatform ? (
          <>
            {getPlatformIcon(selectedPlatform.platform, selectedPlatform.type)}
            <div className="text-left">
              <div className="font-medium text-gray-900">
                {selectedPlatform.name || selectedPlatform.username}
              </div>
              <div className="text-xs text-gray-500">
                {selectedPlatform.platform === 'instagram' ? 'Instagram' : 
                 selectedPlatform.type === 'group' ? 'Groupe' : 'Page'}
              </div>
            </div>
          </>
        ) : (
          <>
            <Building2 className="w-4 h-4 text-gray-400" />
            <div className="text-left">
              <div className="font-medium text-gray-500">Sélectionner une plateforme</div>
              <div className="text-xs text-gray-400">{getTotalPlatforms()} disponibles</div>
            </div>
          </>
        )}
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
          {selectedBusinessManager ? (
            <>
              {/* Business Manager Platforms */}
              <div className="border-b border-gray-200">
                <div className="px-3 py-2 bg-blue-50 border-b border-blue-100">
                  <div className="flex items-center space-x-2">
                    <Building2 className="w-4 h-4 text-blue-600" />
                    <span className="font-medium text-blue-800">Business Manager</span>
                  </div>
                  <div className="text-xs text-blue-600 mt-1">{selectedBusinessManager.name}</div>
                </div>
                
                {renderPlatformGroup(
                  allPlatforms.business_pages, 
                  'Pages Facebook', 
                  'business',
                  'Aucune page disponible'
                )}
                
                {renderPlatformGroup(
                  allPlatforms.business_groups, 
                  'Groupes Facebook', 
                  'business',
                  'Aucun groupe disponible'
                )}
                
                {renderPlatformGroup(
                  allPlatforms.business_instagram, 
                  'Comptes Instagram', 
                  'business',
                  'Aucun compte Instagram connecté'
                )}
              </div>

              {/* Personal Platforms */}
              <div>
                <div className="px-3 py-2 bg-gray-50 border-b border-gray-100">
                  <div className="flex items-center space-x-2">
                    <Users className="w-4 h-4 text-gray-600" />
                    <span className="font-medium text-gray-800">Personnel</span>
                  </div>
                </div>
                
                {renderPlatformGroup(
                  allPlatforms.personal_pages, 
                  'Pages Personnelles', 
                  'personal',
                  'Aucune page personnelle'
                )}
                
                {renderPlatformGroup(
                  allPlatforms.personal_groups, 
                  'Groupes Personnels', 
                  'personal',
                  'Aucun groupe personnel'
                )}
              </div>
            </>
          ) : (
            <div className="p-4 text-center text-gray-500">
              <Building2 className="w-8 h-8 mx-auto mb-2 text-gray-400" />
              <p className="font-medium">Sélectionnez d'abord un Business Manager</p>
              <p className="text-sm">Allez dans l'onglet Configuration pour choisir votre Business Manager</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PlatformSelector;