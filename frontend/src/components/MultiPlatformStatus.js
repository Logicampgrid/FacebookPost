import React from 'react';
import { CheckCircle, XCircle, Users, MessageSquare, Instagram, ExternalLink } from 'lucide-react';

const MultiPlatformStatus = ({ publicationResults, publicationSummary }) => {
  if (!publicationResults || !publicationSummary) {
    return null;
  }

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'instagram':
        return <Instagram className="w-4 h-4" />;
      case 'facebook_group':
        return <MessageSquare className="w-4 h-4" />;
      case 'facebook_page':
        return <Users className="w-4 h-4" />;
      default:
        return <ExternalLink className="w-4 h-4" />;
    }
  };

  const getStatusIcon = (status) => {
    return status === 'success' 
      ? <CheckCircle className="w-4 h-4 text-green-500" />
      : <XCircle className="w-4 h-4 text-red-500" />;
  };

  const getStatusColor = (status) => {
    return status === 'success' 
      ? 'text-green-700 bg-green-50 border-green-200'
      : 'text-red-700 bg-red-50 border-red-200';
  };

  return (
    <div className="mt-4 space-y-4">
      {/* Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-800 mb-2">📊 Résumé de Publication Multi-Plateforme</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-green-600 font-medium">✅ Réussies: {publicationSummary.total_published}</span>
          </div>
          <div>
            <span className="text-red-600 font-medium">❌ Échecs: {publicationSummary.total_failed}</span>
          </div>
        </div>
      </div>

      {/* Main Page */}
      <div className={`border rounded-lg p-3 ${getStatusColor(publicationResults.main_page?.status)}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getPlatformIcon('facebook_page')}
            <span className="font-medium">Page Principale</span>
            {getStatusIcon(publicationResults.main_page?.status)}
          </div>
          <span className="text-xs opacity-75">
            {publicationResults.main_page?.page_name}
          </span>
        </div>
        {publicationResults.main_page?.post_id && (
          <div className="mt-1 text-xs opacity-75">
            ID: {publicationResults.main_page.post_id}
          </div>
        )}
      </div>

      {/* Additional Pages */}
      {publicationResults.additional_pages && publicationResults.additional_pages.length > 0 && (
        <div className="space-y-2">
          <h5 className="font-medium text-gray-700">📄 Pages Additionnelles</h5>
          {publicationResults.additional_pages.map((page, index) => (
            <div key={index} className={`border rounded-lg p-3 ${getStatusColor(page.status)}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getPlatformIcon('facebook_page')}
                  <span className="font-medium">{page.page_name}</span>
                  {getStatusIcon(page.status)}
                </div>
              </div>
              {page.error && (
                <div className="mt-1 text-xs opacity-75">
                  Erreur: {page.error}
                </div>
              )}
              {page.post_id && (
                <div className="mt-1 text-xs opacity-75">
                  ID: {page.post_id}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Groups */}
      {publicationResults.groups && publicationResults.groups.length > 0 && (
        <div className="space-y-2">
          <h5 className="font-medium text-gray-700">👥 Groupes Facebook</h5>
          {publicationResults.groups.map((group, index) => (
            <div key={index} className={`border rounded-lg p-3 ${getStatusColor(group.status)}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getPlatformIcon('facebook_group')}
                  <span className="font-medium">{group.group_name}</span>
                  {getStatusIcon(group.status)}
                </div>
              </div>
              {group.error && (
                <div className="mt-1 text-xs opacity-75">
                  Erreur: {group.error}
                </div>
              )}
              {group.post_id && (
                <div className="mt-1 text-xs opacity-75">
                  ID: {group.post_id}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Instagram Accounts */}
      {publicationResults.instagram_accounts && publicationResults.instagram_accounts.length > 0 && (
        <div className="space-y-2">
          <h5 className="font-medium text-gray-700">📸 Comptes Instagram</h5>
          {publicationResults.instagram_accounts.map((instagram, index) => (
            <div key={index} className={`border rounded-lg p-3 ${getStatusColor(instagram.status)}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getPlatformIcon('instagram')}
                  <span className="font-medium">@{instagram.account_name}</span>
                  {getStatusIcon(instagram.status)}
                </div>
              </div>
              {instagram.error && (
                <div className="mt-1 text-xs opacity-75">
                  Erreur: {instagram.error}
                </div>
              )}
              {instagram.post_id && (
                <div className="mt-1 text-xs opacity-75">
                  ID: {instagram.post_id}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Empty states */}
      {(!publicationResults.additional_pages || publicationResults.additional_pages.length === 0) &&
       (!publicationResults.groups || publicationResults.groups.length === 0) &&
       (!publicationResults.instagram_accounts || publicationResults.instagram_accounts.length === 0) && (
        <div className="text-center py-4 text-gray-500 text-sm">
          <p>📱 Publication sur la page principale uniquement</p>
          <p className="text-xs mt-1">Aucune plateforme additionnelle configurée</p>
        </div>
      )}
    </div>
  );
};

export default MultiPlatformStatus;