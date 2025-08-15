import React, { useState, useEffect } from 'react';
import { Target, Instagram, Users, MessageSquare, ChevronDown, ChevronUp, Sparkles, Zap } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const SmartCrossPostSelector = ({ 
  selectedPlatform, 
  user, 
  onCrossTargetsChange,
  initialTargets = []
}) => {
  const [relatedPlatforms, setRelatedPlatforms] = useState(null);
  const [selectedTargets, setSelectedTargets] = useState(initialTargets);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [smartMode, setSmartMode] = useState(false);

  const getPlatformIcon = (platform, type) => {
    if (platform === 'instagram') return <Instagram className="w-4 h-4 text-pink-500" />;
    if (type === 'group') return <MessageSquare className="w-4 h-4 text-purple-500" />;
    return <Users className="w-4 h-4 text-blue-500" />;
  };

  const loadRelatedPlatforms = async () => {
    if (!selectedPlatform || selectedPlatform.platform !== 'facebook' || selectedPlatform.type !== 'page') {
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get(
        `${API_BASE}/api/pages/${selectedPlatform.id}/related-platforms?user_id=${user._id}`
      );
      
      if (response.data.success) {
        setRelatedPlatforms(response.data.related_platforms);
        
        // Auto-select smart suggestions if in smart mode
        if (smartMode) {
          const autoSelected = response.data.related_platforms.cross_post_suggestions
            .filter(s => s.selected)
            .map(s => ({
              id: s.id,
              name: s.name,
              platform: s.platform,
              type: s.type,
              requires_media: s.requires_media
            }));
          
          setSelectedTargets(autoSelected);
          onCrossTargetsChange(autoSelected);
        }
      }
    } catch (error) {
      console.error('Error loading related platforms:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedPlatform && smartMode) {
      loadRelatedPlatforms();
    }
  }, [selectedPlatform, smartMode, user]);

  const handleSmartModeToggle = () => {
    const newSmartMode = !smartMode;
    setSmartMode(newSmartMode);
    
    if (newSmartMode) {
      loadRelatedPlatforms();
    } else {
      setSelectedTargets([]);
      onCrossTargetsChange([]);
      setRelatedPlatforms(null);
    }
  };

  const handleTargetToggle = (suggestion) => {
    setSelectedTargets(prev => {
      const exists = prev.find(t => t.id === suggestion.id);
      let newTargets;
      
      if (exists) {
        newTargets = prev.filter(t => t.id !== suggestion.id);
      } else {
        newTargets = [...prev, {
          id: suggestion.id,
          name: suggestion.name,
          platform: suggestion.platform,
          type: suggestion.type,
          requires_media: suggestion.requires_media
        }];
      }
      
      onCrossTargetsChange(newTargets);
      return newTargets;
    });
  };

  const getCompatibilityWarnings = () => {
    const warnings = [];
    const instagramTargets = selectedTargets.filter(t => t.platform === 'instagram');
    
    if (instagramTargets.length > 0) {
      warnings.push('Instagram nécessite au moins une image');
    }
    
    return warnings;
  };

  // Don't show for non-Facebook pages
  if (!selectedPlatform || selectedPlatform.platform !== 'facebook' || selectedPlatform.type !== 'page') {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* Smart Mode Toggle */}
      <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="font-medium text-gray-800">Publication Meta Intelligente</h3>
              <p className="text-sm text-gray-600">
                {smartMode ? 
                  'Publication automatique sur Instagram + groupes accessibles' : 
                  'Activez pour publier sur toutes les plateformes liées à cette page'
                }
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleSmartModeToggle}
            disabled={loading}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              smartMode 
                ? 'bg-purple-600 text-white shadow-lg' 
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {loading ? (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-gray-300 border-t-purple-600 rounded-full animate-spin" />
                <span>Chargement...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4" />
                <span>{smartMode ? 'Mode Intelligent' : 'Activer le Mode Intelligent'}</span>
              </div>
            )}
          </button>
        </div>
      </div>

      {/* Smart Suggestions */}
      {smartMode && relatedPlatforms && (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-purple-600" />
                <span className="font-medium text-gray-800">
                  Plateformes suggérées ({selectedTargets.length} sélectionnées)
                </span>
              </div>
              <button
                onClick={() => setExpanded(!expanded)}
                className="text-gray-500 hover:text-gray-700"
              >
                {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className={`transition-all duration-300 ${expanded ? 'max-h-96' : 'max-h-32'} overflow-y-auto`}>
            {relatedPlatforms.cross_post_suggestions.map((suggestion) => {
              const isSelected = selectedTargets.find(t => t.id === suggestion.id);
              const isPrimary = suggestion.primary;
              
              return (
                <div
                  key={suggestion.id}
                  className={`p-3 border-b border-gray-100 last:border-b-0 ${
                    isPrimary ? 'bg-blue-50' : 'bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {getPlatformIcon(suggestion.platform, suggestion.type)}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-gray-900">
                            {suggestion.name}
                          </span>
                          {isPrimary && (
                            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                              Principal
                            </span>
                          )}
                          {suggestion.requires_media && (
                            <span className="px-2 py-1 bg-pink-100 text-pink-800 text-xs rounded-full">
                              Nécessite image
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {suggestion.platform === 'instagram' && 'Instagram Business'}
                          {suggestion.type === 'group' && (
                            <>
                              Groupe {suggestion.privacy}
                              {suggestion.member_count && ` • ${suggestion.member_count} membres`}
                            </>
                          )}
                          {suggestion.type === 'page' && 'Page Facebook'}
                        </div>
                      </div>
                    </div>
                    
                    {!isPrimary && (
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={!!isSelected}
                          onChange={() => handleTargetToggle(suggestion)}
                          className="w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500 focus:ring-2"
                        />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Selected Summary */}
          {selectedTargets.length > 0 && (
            <div className="bg-purple-50 px-4 py-3 border-t border-purple-200">
              <div className="flex items-center justify-between">
                <div className="text-sm text-purple-800">
                  <strong>{selectedTargets.length} plateformes sélectionnées</strong>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedTargets.map((target) => (
                      <span
                        key={target.id}
                        className="inline-flex items-center px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded"
                      >
                        {getPlatformIcon(target.platform, target.type)}
                        <span className="ml-1">{target.name}</span>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Compatibility warnings */}
              {getCompatibilityWarnings().length > 0 && (
                <div className="mt-2 p-2 bg-yellow-100 border border-yellow-200 rounded text-xs text-yellow-800">
                  <strong>⚠️ Attention:</strong>
                  {getCompatibilityWarnings().map((warning, index) => (
                    <div key={index} className="mt-1">• {warning}</div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Summary when not expanded */}
      {smartMode && relatedPlatforms && !expanded && selectedTargets.length > 0 && (
        <div className="text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded">
          Publication prévue sur: {selectedTargets.map(t => t.name).join(', ')}
        </div>
      )}
    </div>
  );
};

export default SmartCrossPostSelector;