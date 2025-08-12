import React, { useState, useEffect } from 'react';
import { Building2, Check, Users, AlertCircle } from 'lucide-react';
import axios from 'axios';

const BusinessManagerSelector = ({ user, onBusinessManagerSelect }) => {
  const [loading, setLoading] = useState(false);
  const [selectedBM, setSelectedBM] = useState(user?.selected_business_manager);
  
  const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

  const handleSelectBusinessManager = async (businessManager) => {
    try {
      setLoading(true);
      
      const response = await axios.post(
        `${API_BASE}/api/users/${user._id}/select-business-manager`,
        { business_manager_id: businessManager.id }
      );
      
      setSelectedBM(businessManager);
      onBusinessManagerSelect && onBusinessManagerSelect(businessManager);
      
    } catch (error) {
      console.error('Error selecting business manager:', error);
      alert('Erreur lors de la sélection du Business Manager');
    } finally {
      setLoading(false);
    }
  };

  const clearSelection = async () => {
    try {
      setLoading(true);
      setSelectedBM(null);
      onBusinessManagerSelect && onBusinessManagerSelect(null);
    } catch (error) {
      console.error('Error clearing selection:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user?.business_managers || user.business_managers.length === 0) {
    return (
      <div className="facebook-card p-6 mb-6">
        <div className="flex items-center space-x-3 mb-4">
          <AlertCircle className="w-6 h-6 text-yellow-500" />
          <div>
            <h3 className="text-lg font-semibold text-yellow-800">Aucun Business Manager trouvé</h3>
            <p className="text-sm text-gray-600">
              Configuration requise pour accéder à "Entreprise de Didier Preud'homme"
            </p>
          </div>
        </div>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <h4 className="font-medium text-yellow-800 mb-3">Causes possibles :</h4>
          <ul className="space-y-2 text-sm text-yellow-700">
            <li className="flex items-start space-x-2">
              <span className="mt-1">•</span>
              <span>La permission <code className="bg-yellow-100 px-1 rounded">business_management</code> n'est pas accordée</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="mt-1">•</span>
              <span>Votre compte n'a pas accès au Business Manager sur Facebook</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="mt-1">•</span>
              <span>Le token Facebook n'a pas les bonnes permissions</span>
            </li>
          </ul>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <h4 className="font-medium text-blue-800 mb-3">Solutions :</h4>
          <div className="space-y-3 text-sm">
            <div className="flex items-start space-x-2">
              <span className="bg-blue-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold mt-0.5">1</span>
              <div>
                <p className="font-medium text-blue-800">Utilisez le diagnostic des permissions</p>
                <p className="text-blue-700">Collez votre token et cliquez sur "Diagnostiquer les Permissions"</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-2">
              <span className="bg-blue-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold mt-0.5">2</span>
              <div>
                <p className="font-medium text-blue-800">Vérifiez vos permissions sur Facebook</p>
                <p className="text-blue-700">Assurez-vous d'avoir accès à "Entreprise de Didier Preud'homme"</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-2">
              <span className="bg-blue-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold mt-0.5">3</span>
              <div>
                <p className="font-medium text-blue-800">Demandez l'approbation business_management</p>
                <p className="text-blue-700">Cette permission peut nécessiter une approbation Facebook</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex space-x-3">
          <a
            href="https://developers.facebook.com/tools/explorer/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-center text-sm"
          >
            📋 Graph API Explorer
          </a>
          <a
            href="https://business.facebook.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors text-center text-sm"
          >
            🏢 Business Manager
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="facebook-card p-6 mb-6">
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
          <Building2 className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-800">Business Manager</h2>
          <p className="text-sm text-gray-600">
            Sélectionnez le portefeuille d'entreprise à utiliser
          </p>
        </div>
      </div>

      {selectedBM && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Check className="w-4 h-4 text-green-600" />
              <span className="text-green-800 font-medium">{selectedBM.name}</span>
              <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded">
                {selectedBM.pages?.length || 0} pages
              </span>
            </div>
            <button
              onClick={clearSelection}
              disabled={loading}
              className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
            >
              Changer
            </button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {user.business_managers.map((bm) => (
          <div
            key={bm.id}
            className={`border rounded-lg p-4 cursor-pointer transition-all ${
              selectedBM?.id === bm.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            }`}
            onClick={() => !loading && handleSelectBusinessManager(bm)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                  <Building2 className="w-4 h-4 text-gray-600" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-800">{bm.name}</h3>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span className="flex items-center space-x-1">
                      <Users className="w-3 h-3" />
                      <span>{bm.pages?.length || 0} pages</span>
                    </span>
                    {bm.verification_status && (
                      <span className={`px-2 py-1 rounded text-xs ${
                        bm.verification_status === 'verified'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {bm.verification_status}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              
              {selectedBM?.id === bm.id && (
                <Check className="w-5 h-5 text-blue-600" />
              )}
            </div>

            {bm.pages && bm.pages.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-100">
                <p className="text-xs text-gray-500 mb-2">Pages disponibles :</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {bm.pages.slice(0, 4).map((page) => (
                    <div key={page.id} className="text-xs bg-gray-100 rounded px-2 py-1">
                      {page.name}
                    </div>
                  ))}
                  {bm.pages.length > 4 && (
                    <div className="text-xs text-gray-500 italic">
                      +{bm.pages.length - 4} autres...
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-4 text-xs text-gray-500">
        💡 <strong>Info :</strong> Sélectionnez le Business Manager "Entreprise de Didier Preud'homme" 
        pour accéder uniquement aux pages de votre portefeuille d'entreprise.
      </div>
    </div>
  );
};

export default BusinessManagerSelector;