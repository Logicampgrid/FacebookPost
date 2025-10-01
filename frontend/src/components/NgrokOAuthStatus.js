import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertCircle, RefreshCw, Settings, Globe, Key } from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

const NgrokOAuthStatus = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [configuring, setConfiguring] = useState(false);

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/config/oauth-status-complete`);
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Erreur récupération status OAuth:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const forceOAuthSetup = async () => {
    try {
      setConfiguring(true);
      const response = await fetch(`${API_BASE}/api/config/force-oauth-setup`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.success) {
        alert('Configuration OAuth mise à jour avec succès !');
        await fetchStatus(); // Rafraîchir le statut
      } else {
        alert(`Erreur configuration OAuth: ${data.error}`);
      }
    } catch (error) {
      console.error('Erreur configuration OAuth:', error);
      alert('Erreur lors de la configuration OAuth');
    } finally {
      setConfiguring(false);
    }
  };

  const refreshStatus = async () => {
    setRefreshing(true);
    await fetchStatus();
  };

  useEffect(() => {
    fetchStatus();
    
    // Rafraîchir automatiquement toutes les 2 minutes (120 secondes) pour réduire le spam
    const interval = setInterval(fetchStatus, 120000);
    
    return () => clearInterval(interval);
  }, []);

  const StatusIndicator = ({ condition, trueIcon: TrueIcon, falseIcon: FalseIcon, label }) => (
    <div className="flex items-center space-x-2">
      {condition ? (
        <TrueIcon className="w-4 h-4 text-green-500" />
      ) : (
        <FalseIcon className="w-4 h-4 text-red-500" />
      )}
      <span className={condition ? 'text-green-700' : 'text-red-700'}>
        {label}
      </span>
    </div>
  );

  if (loading) {
    return (
      <div className="facebook-card p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Settings className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-800">Status Ngrok & OAuth</h3>
        </div>
        <div className="flex items-center space-x-2">
          <RefreshCw className="w-4 h-4 animate-spin" />
          <span>Chargement du statut...</span>
        </div>
      </div>
    );
  }

  const isFullyOperational = status?.oauth_ready && status?.auto_config_completed;

  return (
    <div className="facebook-card p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Settings className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-800">Status Ngrok & OAuth</h3>
          {isFullyOperational && (
            <div className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
              Opérationnel
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={refreshStatus}
            disabled={refreshing}
            className="p-2 text-gray-600 hover:text-gray-800 disabled:opacity-50"
            title="Actualiser"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
          
          <button
            onClick={forceOAuthSetup}
            disabled={configuring}
            className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:opacity-50"
            title="Reconfigurer OAuth"
          >
            {configuring ? 'Configuration...' : 'Reconfigurer'}
          </button>
        </div>
      </div>

      {status?.error ? (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <XCircle className="w-5 h-5 text-red-500" />
            <span className="text-red-800 font-medium">Erreur</span>
          </div>
          <p className="text-red-700 text-sm mt-1">{status.error}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Statut Principal */}
          <div className={`p-4 border rounded-lg ${
            isFullyOperational 
              ? 'bg-green-50 border-green-200' 
              : 'bg-yellow-50 border-yellow-200'
          }`}>
            <div className="flex items-center space-x-2 mb-2">
              {isFullyOperational ? (
                <CheckCircle className="w-5 h-5 text-green-500" />
              ) : (
                <AlertCircle className="w-5 h-5 text-yellow-500" />
              )}
              <span className={`font-medium ${
                isFullyOperational ? 'text-green-800' : 'text-yellow-800'
              }`}>
                {isFullyOperational 
                  ? 'Configuration complète et opérationnelle' 
                  : 'Configuration incomplète ou en cours'
                }
              </span>
            </div>
            
            {status?.ngrok_url && (
              <div className="text-sm text-gray-600">
                <strong>URL Ngrok:</strong> <span className="font-mono">{status.ngrok_url}</span>
              </div>
            )}
          </div>

          {/* Détails de Configuration */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Ngrok Status */}
            <div className="p-3 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-800 mb-2 flex items-center space-x-1">
                <Globe className="w-4 h-4" />
                <span>Tunnel Ngrok</span>
              </h4>
              <div className="space-y-1">
                <StatusIndicator
                  condition={status?.ngrok_active}
                  trueIcon={CheckCircle}
                  falseIcon={XCircle}
                  label={status?.ngrok_active ? 'Actif' : 'Inactif'}
                />
                {status?.ngrok_url && (
                  <div className="text-xs text-gray-600 font-mono">
                    {status.ngrok_url}
                  </div>
                )}
              </div>
            </div>

            {/* Facebook Config */}
            <div className="p-3 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-800 mb-2 flex items-center space-x-1">
                <Key className="w-4 h-4" />
                <span>Configuration Facebook</span>
              </h4>
              <div className="space-y-1 text-sm">
                <StatusIndicator
                  condition={status?.facebook_config?.app_id_configured}
                  trueIcon={CheckCircle}
                  falseIcon={XCircle}
                  label="App ID"
                />
                <StatusIndicator
                  condition={status?.facebook_config?.app_secret_configured}
                  trueIcon={CheckCircle}
                  falseIcon={XCircle}
                  label="App Secret"
                />
                <StatusIndicator
                  condition={status?.facebook_connectivity}
                  trueIcon={CheckCircle}
                  falseIcon={XCircle}
                  label="Connectivité API"
                />
              </div>
            </div>
          </div>

          {/* URLs de Redirection */}
          {status?.redirect_uris_configured?.length > 0 && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-medium text-blue-800 mb-2">URLs de redirection configurées</h4>
              <div className="space-y-1">
                {status.redirect_uris_configured.map((uri, index) => (
                  <div key={index} className="text-sm font-mono text-blue-700">
                    • {uri}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Indicateurs de Santé */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
            <div className={`p-2 rounded text-center ${
              status?.oauth_ready ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {status?.oauth_ready ? '✅' : '❌'} OAuth Ready
            </div>
            
            <div className={`p-2 rounded text-center ${
              status?.auto_config_completed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
              {status?.auto_config_completed ? '✅' : '⚠️'} Auto-Config
            </div>
            
            <div className={`p-2 rounded text-center ${
              status?.facebook_connectivity ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {status?.facebook_connectivity ? '✅' : '❌'} FB API
            </div>
            
            <div className={`p-2 rounded text-center ${
              status?.ngrok_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {status?.ngrok_active ? '✅' : '❌'} Ngrok
            </div>
          </div>

          {/* Dernière Mise à Jour */}
          {status?.timestamp && (
            <div className="text-xs text-gray-500 text-center">
              Dernière mise à jour: {new Date(status.timestamp).toLocaleString('fr-FR')}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NgrokOAuthStatus;