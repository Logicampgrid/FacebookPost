import React, { useState, useEffect } from 'react';
import { Instagram, CheckCircle, AlertCircle, Loader, ExternalLink } from 'lucide-react';

const LogicampBergerSetup = ({ user, onSetupComplete }) => {
  const [setupStatus, setSetupStatus] = useState('checking');
  const [businessManagerFound, setBusinessManagerFound] = useState(false);
  const [instagramFound, setInstagramFound] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    if (user) {
      checkLogicampBergerSetup();
    }
  }, [user]);

  const checkLogicampBergerSetup = async () => {
    try {
      setLoading(true);
      
      // Vérifier si Business Manager 1715327795564432 est connecté
      const businessManagers = user.business_managers || [];
      const targetBM = businessManagers.find(bm => bm.id === '1715327795564432');
      
      if (targetBM) {
        setBusinessManagerFound(true);
        
        // Vérifier si @logicamp_berger est disponible
        const instagramAccounts = targetBM.instagram_accounts || [];
        const logicampIG = instagramAccounts.find(ig => ig.username === 'logicamp_berger');
        
        if (logicampIG) {
          setInstagramFound(true);
          setSetupStatus('ready');
          if (onSetupComplete) onSetupComplete(true);
        } else {
          setSetupStatus('instagram_missing');
        }
      } else {
        setSetupStatus('business_manager_missing');
      }
      
    } catch (error) {
      console.error('Erreur vérification setup:', error);
      setSetupStatus('error');
    } finally {
      setLoading(false);
    }
  };

  const testWebhookConnection = async () => {
    try {
      setLoading(true);
      
      const response = await fetch(`${API_BASE}/api/debug/test-logicamp-berger-webhook`, {
        method: 'POST'
      });
      
      const result = await response.json();
      setTestResult(result);
      
      if (result.success) {
        setSetupStatus('ready');
        if (onSetupComplete) onSetupComplete(true);
      }
      
    } catch (error) {
      console.error('Erreur test webhook:', error);
      setTestResult({
        success: false,
        error: 'Erreur de connexion au test'
      });
    } finally {
      setLoading(false);
    }
  };

  const renderSetupStatus = () => {
    switch (setupStatus) {
      case 'checking':
        return (
          <div className="flex items-center space-x-2 text-blue-600">
            <Loader className="w-5 h-5 animate-spin" />
            <span>Vérification configuration @logicamp_berger...</span>
          </div>
        );

      case 'business_manager_missing':
        return (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center space-x-2 text-red-600 mb-4">
              <AlertCircle className="w-5 h-5" />
              <span className="font-semibold">Business Manager Requis</span>
            </div>
            <p className="text-gray-700 mb-4">
              Le Business Manager <strong>1715327795564432</strong> n'est pas connecté à votre compte.
            </p>
            <div className="bg-white border rounded-lg p-4">
              <h4 className="font-semibold mb-2">📋 Instructions :</h4>
              <ol className="list-decimal list-inside space-y-2 text-sm">
                <li>Connectez-vous avec le compte ayant accès au Business Manager <code>1715327795564432</code></li>
                <li>Ou demandez l'accès depuis <a href="https://business.facebook.com" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">Facebook Business Manager</a></li>
                <li>Puis reconnectez-vous à cette application</li>
              </ol>
            </div>
          </div>
        );

      case 'instagram_missing':
        return (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="flex items-center space-x-2 text-yellow-600 mb-4">
              <Instagram className="w-5 h-5" />
              <span className="font-semibold">@logicamp_berger Non Trouvé</span>
            </div>
            <p className="text-gray-700 mb-4">
              Business Manager trouvé, mais @logicamp_berger n'est pas connecté.
            </p>
            <div className="bg-white border rounded-lg p-4">
              <h4 className="font-semibold mb-2">📱 Instructions :</h4>
              <ol className="list-decimal list-inside space-y-2 text-sm">
                <li>Allez sur <a href="https://business.facebook.com" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">Facebook Business Manager</a></li>
                <li>Dans "Comptes" → "Instagram", connectez @logicamp_berger</li>
                <li>Assurez-vous que c'est un compte Instagram Business</li>
                <li>Reconnectez-vous à cette application</li>
              </ol>
            </div>
          </div>
        );

      case 'ready':
        return (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center space-x-2 text-green-600 mb-4">
              <CheckCircle className="w-5 h-5" />
              <span className="font-semibold">✅ Configuration Prête !</span>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-white border rounded-lg p-4">
                <h4 className="font-semibold flex items-center space-x-2 mb-2">
                  <Instagram className="w-4 h-4" />
                  <span>Instagram @logicamp_berger</span>
                </h4>
                <p className="text-sm text-gray-600">
                  ✅ Connecté et prêt pour les publications webhook gizmobbs
                </p>
                <a 
                  href="https://www.instagram.com/logicamp_berger/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-1 text-blue-600 hover:underline text-sm mt-2"
                >
                  <span>Voir le profil</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <div className="bg-white border rounded-lg p-4">
                <h4 className="font-semibold mb-2">🚀 Webhook Endpoint</h4>
                <p className="text-sm text-gray-600 mb-2">
                  <code className="bg-gray-100 px-2 py-1 rounded">shop_type: "gizmobbs"</code>
                </p>
                <p className="text-xs text-gray-500">
                  Publiera automatiquement sur @logicamp_berger
                </p>
              </div>
            </div>
          </div>
        );

      case 'error':
      default:
        return (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center space-x-2 text-red-600 mb-4">
              <AlertCircle className="w-5 h-5" />
              <span className="font-semibold">Erreur Configuration</span>
            </div>
            <p className="text-gray-700">
              Impossible de vérifier la configuration @logicamp_berger.
            </p>
          </div>
        );
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Configuration @logicamp_berger
        </h1>
        <p className="text-gray-600">
          Configuration spéciale pour publier sur Instagram @logicamp_berger via webhook gizmobbs
        </p>
      </div>

      {renderSetupStatus()}

      {setupStatus === 'ready' && (
        <div className="mt-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="font-semibold text-blue-900 mb-3">🧪 Test de Publication</h3>
            <p className="text-blue-700 mb-4">
              Testez que votre webhook peut publier sur @logicamp_berger
            </p>
            <button
              onClick={testWebhookConnection}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
            >
              {loading ? (
                <Loader className="w-4 h-4 animate-spin" />
              ) : (
                <Instagram className="w-4 h-4" />
              )}
              <span>Tester Publication @logicamp_berger</span>
            </button>
          </div>

          {testResult && (
            <div className={`mt-4 border rounded-lg p-4 ${
              testResult.success 
                ? 'bg-green-50 border-green-200' 
                : 'bg-red-50 border-red-200'
            }`}>
              <h4 className={`font-semibold mb-2 ${
                testResult.success ? 'text-green-900' : 'text-red-900'
              }`}>
                {testResult.success ? '✅ Test Réussi !' : '❌ Test Échoué'}
              </h4>
              <pre className="text-xs bg-white border rounded p-2 overflow-auto">
                {JSON.stringify(testResult, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}

      <div className="mt-8 bg-gray-50 border rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-3">📖 Guide Webhook Gizmobbs</h3>
        <div className="space-y-4 text-sm">
          <div>
            <h4 className="font-medium text-gray-700">Endpoint :</h4>
            <code className="bg-white border rounded px-2 py-1">
              POST {API_BASE}/api/webhook
            </code>
          </div>
          <div>
            <h4 className="font-medium text-gray-700">Format JSON :</h4>
            <pre className="bg-white border rounded p-3 overflow-auto text-xs">
{`{
  "title": "Mon Produit",
  "description": "Description du produit",
  "url": "https://gizmobbs.com/produit",
  "store": "gizmobbs"
}`}</pre>
          </div>
          <div className="bg-blue-100 border border-blue-300 rounded p-3">
            <p className="text-blue-800 font-medium">
              🎯 Avec <code>store: "gizmobbs"</code>, vos produits seront automatiquement publiés sur @logicamp_berger !
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogicampBergerSetup;