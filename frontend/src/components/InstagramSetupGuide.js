import React from 'react';
import { 
  Instagram, 
  Facebook, 
  User, 
  Settings, 
  CheckCircle, 
  AlertCircle, 
  ArrowRight,
  ExternalLink
} from 'lucide-react';

const InstagramSetupGuide = () => {
  const steps = [
    {
      id: 1,
      title: "Authentification Facebook",
      description: "Connectez-vous avec votre compte Facebook Business Manager",
      icon: <User className="w-5 h-5" />,
      status: "primary",
      actions: [
        "Cliquer sur le bouton 'Facebook Login'",
        "Choisir le compte avec accès au Business Manager", 
        "Accepter toutes les permissions demandées"
      ]
    },
    {
      id: 2, 
      title: "Sélection Business Manager",
      description: "Choisissez le Business Manager approprié",
      icon: <Settings className="w-5 h-5" />,
      status: "secondary",
      actions: [
        "Sélectionner 'Entreprise de Didier Preud'homme' (si disponible)",
        "Ou choisir le Business Manager avec accès Instagram",
        "Vérifier que les pages et comptes apparaissent"
      ]
    },
    {
      id: 3,
      title: "Vérification Instagram", 
      description: "Confirmez que les comptes Instagram Business sont connectés",
      icon: <Instagram className="w-5 h-5" />,
      status: "success",
      actions: [
        "Vérifier la détection automatique des comptes Instagram",
        "S'assurer que @logicamp_berger est connecté",
        "Confirmer les permissions de publication"
      ]
    },
    {
      id: 4,
      title: "Test de Publication",
      description: "Testez la publication pour confirmer le bon fonctionnement",
      icon: <CheckCircle className="w-5 h-5" />,
      status: "warning",
      actions: [
        "Utiliser le bouton 'Test Publication' dans les diagnostics",
        "Vérifier qu'un post de test est créé sur Instagram",
        "Confirmer que la publication multi-plateforme fonctionne"
      ]
    }
  ];

  const getStatusColor = (status) => {
    switch(status) {
      case 'primary': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'secondary': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'success': return 'bg-green-100 text-green-800 border-green-200';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-3 mb-4">
          <div className="p-3 bg-gradient-to-r from-pink-500 to-purple-600 rounded-full">
            <Instagram className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">
            Guide de Configuration Instagram
          </h1>
        </div>
        <p className="text-xl text-gray-600">
          Configurez la publication automatique sur Instagram en 4 étapes simples
        </p>
      </div>

      {/* Problem Summary */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-3 mb-3">
          <AlertCircle className="w-6 h-6 text-red-600" />
          <h2 className="text-lg font-semibold text-red-800">Problème Identifié</h2>
        </div>
        <div className="space-y-2 text-red-700">
          <p>✅ <strong>Configuration technique</strong> : Correcte</p>
          <p>✅ <strong>Code Instagram</strong> : Fonctionnel</p>
          <p>✅ <strong>API Instagram</strong> : Implémentée</p>
          <p>❌ <strong>Authentification</strong> : Manquante</p>
        </div>
        <div className="mt-4 p-3 bg-red-100 rounded-lg">
          <p className="text-red-800 font-medium">
            🎯 Solution : Authentification avec Facebook Business Manager requis
          </p>
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900 text-center">
          Étapes de Configuration
        </h2>
        
        {steps.map((step, index) => (
          <div key={step.id} className="relative">
            {/* Connector line */}
            {index < steps.length - 1 && (
              <div className="absolute left-8 top-16 w-0.5 h-16 bg-gray-300"></div>
            )}
            
            <div className={`border rounded-lg p-6 ${getStatusColor(step.status)}`}>
              <div className="flex items-start space-x-4">
                {/* Step number and icon */}
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 rounded-full bg-white flex items-center justify-center border-2 border-current">
                    <div className="text-center">
                      <div className="text-xs font-bold">{step.id}</div>
                      <div className="mt-1">{step.icon}</div>
                    </div>
                  </div>
                </div>
                
                {/* Content */}
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                  <p className="text-base mb-4">{step.description}</p>
                  
                  <ul className="space-y-2">
                    {step.actions.map((action, actionIndex) => (
                      <li key={actionIndex} className="flex items-center space-x-2">
                        <ArrowRight className="w-4 h-4 flex-shrink-0" />
                        <span className="text-sm">{action}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Expected Configuration */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-800 mb-4">
          📱 Configuration Attendue (Gizmobbs)
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <Facebook className="w-5 h-5 text-blue-600" />
              <div>
                <div className="font-medium">Page Facebook</div>
                <div className="text-sm text-gray-600">"Le Berger Blanc Suisse"</div>
                <div className="text-xs text-gray-500">ID: 102401876209415</div>
              </div>
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <Instagram className="w-5 h-5 text-pink-600" />
              <div>
                <div className="font-medium">Compte Instagram</div>
                <div className="text-sm text-gray-600">@logicamp_berger</div>
                <div className="text-xs text-gray-500">Type: Business</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Troubleshooting */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-yellow-800 mb-4">
          🔧 Dépannage Rapide
        </h3>
        <div className="space-y-3 text-yellow-700">
          <div>
            <strong>Erreur "No authenticated user"</strong>
            <p className="text-sm">→ Se connecter avec Facebook dans l'onglet Configuration</p>
          </div>
          <div>
            <strong>Erreur "No Instagram Business account"</strong>  
            <p className="text-sm">→ Connecter Instagram à la page Facebook dans Business Manager</p>
          </div>
          <div>
            <strong>Erreur "Permission denied"</strong>
            <p className="text-sm">→ Réautoriser toutes les permissions Facebook</p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button 
          onClick={() => window.location.href = '/'}
          className="flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Settings className="w-5 h-5" />
          <span>Aller à Configuration</span>
        </button>
        
        <a 
          href="https://business.facebook.com" 
          target="_blank" 
          rel="noopener noreferrer"
          className="flex items-center justify-center space-x-2 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          <ExternalLink className="w-5 h-5" />
          <span>Business Manager</span>
        </a>
      </div>

      {/* Success Message */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-green-800 mb-2">
          🎉 Résultat Final
        </h3>
        <p className="text-green-700">
          Une fois configuré, l'application publiera automatiquement sur Instagram 
          et Facebook simultanément pour tous les produits Gizmobbs !
        </p>
      </div>
    </div>
  );
};

export default InstagramSetupGuide;