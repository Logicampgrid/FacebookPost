import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, RefreshCw, AlertTriangle, Wifi, Database, Users, Globe } from 'lucide-react';

const ConnectionDiagnostic = ({ API_BASE }) => {
  const [tests, setTests] = useState({
    backend: { status: 'pending', message: '', details: null },
    database: { status: 'pending', message: '', details: null },
    facebook: { status: 'pending', message: '', details: null },
    internet: { status: 'pending', message: '', details: null }
  });
  const [testing, setTesting] = useState(false);

  const runTest = async (testName, testFunction) => {
    setTests(prev => ({
      ...prev,
      [testName]: { status: 'running', message: 'Test en cours...', details: null }
    }));

    try {
      const result = await testFunction();
      setTests(prev => ({
        ...prev,
        [testName]: { status: 'success', message: result.message, details: result.details }
      }));
    } catch (error) {
      setTests(prev => ({
        ...prev,
        [testName]: { status: 'error', message: error.message, details: error.details || null }
      }));
    }
  };

  const testBackendConnection = async () => {
    const response = await fetch(`${API_BASE}/api/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) {
      throw new Error(`Backend inaccessible: HTTP ${response.status}`);
    }

    const data = await response.json();
    return {
      message: `Backend connecté - ${data.status}`,
      details: {
        timestamp: data.timestamp,
        database_users: data.database?.users_count || 0,
        database_posts: data.database?.posts_count || 0
      }
    };
  };

  const testDatabaseConnection = async () => {
    const response = await fetch(`${API_BASE}/api/health`);
    const data = await response.json();
    
    if (data.mongodb !== 'connected') {
      throw new Error(`Base de données déconnectée: ${data.mongodb}`);
    }

    return {
      message: `MongoDB connectée - ${data.database.users_count} utilisateurs, ${data.database.posts_count} posts`,
      details: data.database
    };
  };

  const testFacebookConnection = async () => {
    try {
      const response = await fetch('https://graph.facebook.com/v18.0/me?access_token=test&fields=id');
      const data = await response.json();
      
      if (data.error && data.error.code === 190) {
        return {
          message: 'API Facebook accessible (token requis pour authentification)',
          details: { api_accessible: true, requires_auth: true }
        };
      }
      
      throw new Error(`Erreur API Facebook: ${data.error?.message || 'Réponse inattendue'}`);
    } catch (networkError) {
      if (networkError.message.includes('Failed to fetch')) {
        throw new Error('Impossible d\'accéder à l\'API Facebook - problème réseau');
      }
      throw networkError;
    }
  };

  const testInternetConnection = async () => {
    const response = await fetch('https://www.google.com/favicon.ico', { 
      method: 'HEAD',
      mode: 'no-cors'
    });
    
    return {
      message: 'Connexion Internet active',
      details: { internet_available: true }
    };
  };

  const runAllTests = async () => {
    setTesting(true);
    
    await runTest('backend', testBackendConnection);
    await runTest('database', testDatabaseConnection);  
    await runTest('facebook', testFacebookConnection);
    await runTest('internet', testInternetConnection);
    
    setTesting(false);
  };

  useEffect(() => {
    runAllTests();
  }, [API_BASE]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error': return <XCircle className="w-5 h-5 text-red-500" />;
      case 'running': return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      default: return <AlertTriangle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'border-green-200 bg-green-50';
      case 'error': return 'border-red-200 bg-red-50';
      case 'running': return 'border-blue-200 bg-blue-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800">Diagnostic de Connexion</h3>
        <button
          onClick={runAllTests}
          disabled={testing}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 flex items-center space-x-2"
        >
          <RefreshCw className={`w-4 h-4 ${testing ? 'animate-spin' : ''}`} />
          <span>Relancer les Tests</span>
        </button>
      </div>

      <div className="grid gap-4">
        {/* Backend Test */}
        <div className={`p-4 rounded-lg border ${getStatusColor(tests.backend.status)}`}>
          <div className="flex items-center space-x-3">
            <Wifi className="w-5 h-5 text-gray-600" />
            {getStatusIcon(tests.backend.status)}
            <div className="flex-1">
              <h4 className="font-medium">Connexion Backend</h4>
              <p className="text-sm text-gray-600">{tests.backend.message}</p>
              {tests.backend.details && (
                <div className="text-xs text-gray-500 mt-1">
                  API URL: {API_BASE}/api/health
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Database Test */}
        <div className={`p-4 rounded-lg border ${getStatusColor(tests.database.status)}`}>
          <div className="flex items-center space-x-3">
            <Database className="w-5 h-5 text-gray-600" />
            {getStatusIcon(tests.database.status)}
            <div className="flex-1">
              <h4 className="font-medium">Base de Données MongoDB</h4>
              <p className="text-sm text-gray-600">{tests.database.message}</p>
              {tests.database.details && (
                <div className="text-xs text-gray-500 mt-1">
                  Utilisateurs: {tests.database.details.users_count} | Posts: {tests.database.details.posts_count}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Facebook API Test */}
        <div className={`p-4 rounded-lg border ${getStatusColor(tests.facebook.status)}`}>
          <div className="flex items-center space-x-3">
            <Users className="w-5 h-5 text-gray-600" />
            {getStatusIcon(tests.facebook.status)}
            <div className="flex-1">
              <h4 className="font-medium">API Facebook/Meta</h4>
              <p className="text-sm text-gray-600">{tests.facebook.message}</p>
              <div className="text-xs text-gray-500 mt-1">
                Graph API v18.0
              </div>
            </div>
          </div>
        </div>

        {/* Internet Test */}
        <div className={`p-4 rounded-lg border ${getStatusColor(tests.internet.status)}`}>
          <div className="flex items-center space-x-3">
            <Globe className="w-5 h-5 text-gray-600" />
            {getStatusIcon(tests.internet.status)}
            <div className="flex-1">
              <h4 className="font-medium">Connexion Internet</h4>
              <p className="text-sm text-gray-600">{tests.internet.message}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Overall Status */}
      <div className={`p-4 rounded-lg border ${
        Object.values(tests).every(test => test.status === 'success')
          ? 'border-green-200 bg-green-50'
          : Object.values(tests).some(test => test.status === 'error')
          ? 'border-red-200 bg-red-50'
          : 'border-yellow-200 bg-yellow-50'
      }`}>
        <div className="flex items-center space-x-2">
          {Object.values(tests).every(test => test.status === 'success') ? (
            <>
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="font-medium text-green-800">✅ Toutes les connexions sont opérationnelles</span>
            </>
          ) : Object.values(tests).some(test => test.status === 'error') ? (
            <>
              <XCircle className="w-5 h-5 text-red-500" />
              <span className="font-medium text-red-800">❌ Des problèmes de connexion ont été détectés</span>
            </>
          ) : (
            <>
              <RefreshCw className="w-5 h-5 text-yellow-500" />
              <span className="font-medium text-yellow-800">⏳ Tests en cours...</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConnectionDiagnostic;