import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, RefreshCw } from 'lucide-react';

const ConnectionStatus = ({ API_BASE }) => {
  const [status, setStatus] = useState('checking');
  const [error, setError] = useState('');

  const checkConnection = async () => {
    try {
      setStatus('checking');
      setError('');
      
      const response = await fetch(`${API_BASE}/api/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Backend health check:', data);
        setStatus('connected');
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
    } catch (err) {
      console.error('Connection check failed:', err);
      setStatus('disconnected');
      setError(err.message);
    }
  };

  useEffect(() => {
    checkConnection();
  }, [API_BASE]);

  return (
    <div className="mb-4 p-3 rounded-lg border">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {status === 'checking' && (
            <>
              <RefreshCw className="w-4 h-4 animate-spin text-blue-500" />
              <span className="text-sm text-blue-600">Vérification de la connexion...</span>
            </>
          )}
          {status === 'connected' && (
            <>
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-sm text-green-600">Connecté au serveur</span>
            </>
          )}
          {status === 'disconnected' && (
            <>
              <XCircle className="w-4 h-4 text-red-500" />
              <span className="text-sm text-red-600">Connexion échouée</span>
            </>
          )}
        </div>
        
        <button
          onClick={checkConnection}
          className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
        >
          Tester
        </button>
      </div>
      
      {error && (
        <div className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
          <strong>Erreur:</strong> {error}
        </div>
      )}
      
      <div className="mt-2 text-xs text-gray-500">
        Endpoint: {API_BASE}/api/health
      </div>
    </div>
  );
};

export default ConnectionStatus;