import React, { useState, useEffect } from 'react';
import { Instagram, Users, AlertCircle, CheckCircle, Loader, RefreshCw } from 'lucide-react';
import axios from 'axios';

const InstagramDiagnostics = ({ API_BASE }) => {
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    runDiagnostic();
  }, []);

  const runDiagnostic = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await axios.get(`${API_BASE}/api/debug/instagram-complete-diagnosis`);
      console.log('Instagram diagnosis response:', response.data);
      setDiagnosis(response.data);
      
    } catch (err) {
      console.error('Instagram diagnostic error:', err);
      setError(`Erreur diagnostic: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (isError) => {
    return isError ? 
      <AlertCircle className="w-4 h-4 text-red-500" /> : 
      <CheckCircle className="w-4 h-4 text-green-500" />;
  };

  const getStatusColor = (isError) => {
    return isError ? 'text-red-600' : 'text-green-600';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800 flex items-center space-x-2">
          <Instagram className="w-5 h-5 text-pink-500" />
          <span>Diagnostic Instagram</span>
        </h3>
        
        <button
          onClick={runDiagnostic}
          disabled={loading}
          className="flex items-center space-x-2 px-3 py-1 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 disabled:opacity-50"
        >
          {loading ? (
            <Loader className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          <span>Actualiser</span>
        </button>
      </div>

      {error && (
        <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center space-x-2 p-6 bg-gray-50 rounded-lg">
          <Loader className="w-5 h-5 animate-spin text-gray-400" />
          <span className="text-gray-600">Analyse en cours...</span>
        </div>
      )}

      {diagnosis && !loading && (
        <div className="space-y-6">
          {/* Authentication Status - CORRECTION CRITIQUE */}
          <div className="p-4 border border-gray-200 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">👤 Authentication Status</h4>
            <div className="space-y-2">
              {diagnosis.authentication && diagnosis.authentication.user_found !== undefined ? (
                <>
                  <div className={`flex items-center space-x-2 ${getStatusColor(!diagnosis.authentication.user_found)}`}>
                    {getStatusIcon(!diagnosis.authentication.user_found)}
                    <span>
                      {diagnosis.authentication.user_found 
                        ? `✅ User authenticated: ${diagnosis.authentication.user_name || 'Unknown'}`
                        : '❌ No authenticated user found'
                      }
                    </span>
                  </div>
                  
                  {diagnosis.authentication.user_found && (
                    <div className={`flex items-center space-x-2 ${getStatusColor((diagnosis.authentication.business_managers_count || 0) === 0)}`}>
                      {getStatusIcon((diagnosis.authentication.business_managers_count || 0) === 0)}
                      <span>
                        Business Managers: {diagnosis.authentication.business_managers_count || 0}
                      </span>
                    </div>
                  )}
                </>
              ) : (
                <div className="flex items-center space-x-2 text-yellow-600">
                  <AlertCircle className="w-4 h-4" />
                  <span>Authentication data not available - Please authenticate first</span>
                </div>
              )}
            </div>
          </div>

          {/* Instagram Accounts */}
          <div className="p-4 border border-gray-200 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">📱 Instagram Accounts</h4>
            
            {diagnosis.instagram_accounts && diagnosis.instagram_accounts.length > 0 ? (
              <div className="space-y-3">
                {diagnosis.instagram_accounts.map((account, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Instagram className="w-5 h-5 text-pink-500" />
                      <div>
                        <div className="font-medium">@{account.username}</div>
                        <div className="text-sm text-gray-500">{account.name}</div>
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      ID: {account.id}
                    </div>
                  </div>
                ))}
                
                {/* Logicamp Berger Status */}
                {(() => {
                  const logicampAccount = diagnosis.instagram_accounts.find(
                    account => account.username === 'logicamp_berger'
                  );
                  return (
                    <div className={`p-3 rounded-lg border-2 ${
                      logicampAccount 
                        ? 'bg-green-50 border-green-200' 
                        : 'bg-yellow-50 border-yellow-200'
                    }`}>
                      <div className="flex items-center space-x-2">
                        {logicampAccount ? (
                          <>
                            <CheckCircle className="w-5 h-5 text-green-500" />
                            <span className="font-medium text-green-800">
                              🎯 @logicamp_berger connecté - Tunnel actif !
                            </span>
                          </>
                        ) : (
                          <>
                            <AlertCircle className="w-5 h-5 text-yellow-500" />
                            <span className="font-medium text-yellow-800">
                              ⚠️ @logicamp_berger non trouvé
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  );
                })()}
              </div>
            ) : (
              <div className="flex items-center space-x-2 text-yellow-600">
                <AlertCircle className="w-4 h-4" />
                <span>Aucun compte Instagram connecté</span>
              </div>
            )}
          </div>

          {/* Configuration Status */}
          <div className="p-4 border border-gray-200 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">⚙️ Configuration</h4>
            <div className="space-y-2">
              <div className={`flex items-center space-x-2 ${getStatusColor(!diagnosis.ngrok_active)}`}>
                {getStatusIcon(!diagnosis.ngrok_active)}
                <span>Ngrok Status: {diagnosis.ngrok_active ? '✅ Active' : '❌ Inactive'}</span>
              </div>
              
              {diagnosis.ngrok_url && (
                <div className="flex items-center space-x-2 text-blue-600">
                  <span className="text-sm">🌐 Tunnel URL: {diagnosis.ngrok_url}</span>
                </div>
              )}
              
              <div className={`flex items-center space-x-2 ${getStatusColor(!diagnosis.webhook_configured)}`}>
                {getStatusIcon(!diagnosis.webhook_configured)}
                <span>Webhook: {diagnosis.webhook_configured ? '✅ Configured' : '❌ Not configured'}</span>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="font-medium text-blue-800 mb-2">📊 Résumé</h4>
            <div className="text-sm text-blue-700 space-y-1">
              <p>• Pages Facebook: {diagnosis.facebook_pages_count || 0}</p>
              <p>• Comptes Instagram: {(diagnosis.instagram_accounts && diagnosis.instagram_accounts.length) || 0}</p>
              <p>• Business Managers: {(diagnosis.authentication && diagnosis.authentication.business_managers_count) || 0}</p>
              <p>• Tunnel Status: {diagnosis.ngrok_active ? 'Actif' : 'Inactif'}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InstagramDiagnostics;