import React, { useState, useEffect } from 'react';
import { Instagram, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';
import axios from 'axios';

const TunnelStatusWidget = ({ user }) => {
  const [tunnelStatus, setTunnelStatus] = useState('checking');
  const [instagramAccounts, setInstagramAccounts] = useState([]);

  const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

  useEffect(() => {
    if (user) {
      checkTunnelStatus();
    }
  }, [user]);

  const checkTunnelStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/debug/instagram-complete-diagnosis`);
      const diagnosis = response.data;
      
      if (diagnosis.instagram_accounts && diagnosis.instagram_accounts.length > 0) {
        setInstagramAccounts(diagnosis.instagram_accounts);
        
        const hasLogicampBerger = diagnosis.instagram_accounts.some(
          account => account.username === 'logicamp_berger'
        );
        
        setTunnelStatus(hasLogicampBerger ? 'ready' : 'no_logicamp');
      } else {
        setTunnelStatus('no_instagram');
      }
    } catch (error) {
      console.error('Erreur check tunnel status:', error);
      setTunnelStatus('error');
    }
  };

  if (tunnelStatus === 'ready') {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <Instagram className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-green-900">Tunnel Instagram Actif</h3>
              <p className="text-sm text-green-700">@logicamp_berger connecté</p>
            </div>
          </div>
          <CheckCircle className="w-5 h-5 text-green-600" />
        </div>
      </div>
    );
  }

  if (tunnelStatus === 'no_instagram' || tunnelStatus === 'no_logicamp') {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <h3 className="font-semibold text-yellow-900">
                {tunnelStatus === 'no_instagram' ? 'Tunnel Instagram Inactif' : '@logicamp_berger Manquant'}
              </h3>
              <p className="text-sm text-yellow-700">
                {tunnelStatus === 'no_instagram' 
                  ? 'Aucun compte Instagram connecté' 
                  : `${instagramAccounts.length} compte(s) trouvé(s), mais pas @logicamp_berger`
                }
              </p>
            </div>
          </div>
          <ArrowRight className="w-5 h-5 text-yellow-600" />
        </div>
        <div className="mt-3 pt-3 border-t border-yellow-200">
          <p className="text-xs text-yellow-700">
            Activez le tunnel dans l'onglet "Tunnel Instagram" pour publier automatiquement sur Instagram
          </p>
        </div>
      </div>
    );
  }

  if (tunnelStatus === 'checking') {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
          <div>
            <h3 className="font-semibold text-blue-900">Vérification Tunnel Instagram</h3>
            <p className="text-sm text-blue-700">Analyse des comptes connectés...</p>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default TunnelStatusWidget;