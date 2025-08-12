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
      <div className="facebook-card p-4 mb-6">
        <div className="flex items-center space-x-3 text-yellow-600">
          <AlertCircle className="w-5 h-5" />
          <div>
            <h3 className="font-medium">Aucun Business Manager trouvé</h3>
            <p className="text-sm text-gray-600">
              Vous devez avoir accès à un Business Manager pour utiliser cette fonctionnalité
            </p>
          </div>
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