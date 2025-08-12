import React, { useState } from 'react';
import { AlertCircle, CheckCircle, XCircle, Search, ExternalLink } from 'lucide-react';
import axios from 'axios';

const PermissionDiagnostic = ({ token, onClose }) => {
  const [diagnostic, setDiagnostic] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

  const runDiagnostic = async () => {
    if (!token) {
      alert('Aucun token à analyser');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/api/debug/permissions/${encodeURIComponent(token)}`);
      setDiagnostic(response.data);
    } catch (error) {
      console.error('Error running diagnostic:', error);
      setDiagnostic({
        status: 'error',
        error: error.response?.data || error.message
      });
    } finally {
      setLoading(false);
    }
  };

  const getPermissionIcon = (permission) => {
    const required = ['pages_manage_posts', 'pages_read_engagement', 'pages_show_list', 'business_management'];
    if (required.includes(permission)) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
    return <div className="w-4 h-4 rounded-full bg-gray-300" />;
  };

  const getRecommendationIcon = (type) => {
    switch (type) {
      case 'missing_permissions':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'business_management':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'account_access':
        return <CheckCircle className="w-5 h-5 text-blue-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Search className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-semibold">Diagnostic des Permissions Facebook</h2>
            </div>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
        </div>

        <div className="p-6">
          {!diagnostic ? (
            <div className="text-center">
              <p className="text-gray-600 mb-4">
                Analyser les permissions du token pour diagnostiquer le problème Business Manager
              </p>
              <button
                onClick={runDiagnostic}
                disabled={loading}
                className="facebook-button flex items-center space-x-2 mx-auto"
              >
                {loading ? (
                  <>
                    <div className="spinner" />
                    <span>Analyse en cours...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    <span>Analyser les Permissions</span>
                  </>
                )}
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {diagnostic.status === 'error' ? (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <XCircle className="w-5 h-5 text-red-500" />
                    <span className="font-medium text-red-800">Erreur d'analyse</span>
                  </div>
                  <p className="text-red-700 mt-2">{JSON.stringify(diagnostic.error)}</p>
                </div>
              ) : (
                <>
                  {/* Permission Status */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="font-medium text-blue-800 mb-3">Statut des Permissions</h3>
                    <div className="flex items-center space-x-4 mb-2">
                      <span className="text-sm">Business Management:</span>
                      {diagnostic.has_business_management ? (
                        <div className="flex items-center space-x-1 text-green-600">
                          <CheckCircle className="w-4 h-4" />
                          <span className="text-sm">Accordée</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-1 text-red-600">
                          <XCircle className="w-4 h-4" />
                          <span className="text-sm">Manquante</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Granted Permissions */}
                  <div>
                    <h3 className="font-medium text-gray-800 mb-3">Permissions Accordées ({diagnostic.granted_permissions.length})</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {diagnostic.granted_permissions.map((permission) => (
                        <div key={permission} className="flex items-center space-x-2 text-sm">
                          {getPermissionIcon(permission)}
                          <span>{permission}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Declined Permissions */}
                  {diagnostic.declined_permissions.length > 0 && (
                    <div>
                      <h3 className="font-medium text-gray-800 mb-3">Permissions Refusées</h3>
                      <div className="space-y-2">
                        {diagnostic.declined_permissions.map((item, index) => (
                          <div key={index} className="flex items-center space-x-2 text-sm text-red-600">
                            <XCircle className="w-4 h-4" />
                            <span>{item.permission} ({item.status})</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Business API Test */}
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h3 className="font-medium text-gray-800 mb-3">Test API Business Manager</h3>
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm">Code de réponse:</span>
                        <span className={`text-sm font-mono px-2 py-1 rounded ${
                          diagnostic.business_api_test.status_code === 200 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {diagnostic.business_api_test.status_code}
                        </span>
                      </div>
                      {diagnostic.business_api_test.error && (
                        <div className="bg-red-100 border border-red-200 rounded p-2">
                          <p className="text-red-800 text-sm font-mono">
                            {JSON.stringify(diagnostic.business_api_test.error, null, 2)}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div>
                    <h3 className="font-medium text-gray-800 mb-3">Recommandations</h3>
                    <div className="space-y-3">
                      {diagnostic.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg">
                          {getRecommendationIcon(rec.type)}
                          <div className="flex-1">
                            <p className="text-sm font-medium text-gray-800">{rec.message}</p>
                            <p className="text-xs text-gray-600 mt-1">{rec.action}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="border-t pt-4 space-y-3">
                    <a
                      href="https://developers.facebook.com/tools/explorer/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
                    >
                      <ExternalLink className="w-4 h-4" />
                      <span>Ouvrir Graph API Explorer</span>
                    </a>
                    
                    <a
                      href="https://business.facebook.com/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors flex items-center justify-center space-x-2"
                    >
                      <ExternalLink className="w-4 h-4" />
                      <span>Vérifier Business Manager</span>
                    </a>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PermissionDiagnostic;