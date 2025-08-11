import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Hook personnalisé pour détecter et récupérer les métadonnées des liens
export const useLinkDetection = (text, debounceMs = 1000) => {
  const [detectedLinks, setDetectedLinks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [removedLinks, setRemovedLinks] = useState(new Set());

  useEffect(() => {
    if (!text || text.trim().length === 0) {
      setDetectedLinks([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setLoading(true);
        
        const response = await axios.post(`${API_BASE}/api/text/extract-links`, {
          text: text
        });

        const newLinks = response.data.links || [];
        
        // Filtrer les liens supprimés manuellement
        const filteredLinks = newLinks.filter(link => !removedLinks.has(link.url));
        
        setDetectedLinks(filteredLinks);
      } catch (error) {
        console.error('Error detecting links:', error);
        setDetectedLinks([]);
      } finally {
        setLoading(false);
      }
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [text, debounceMs, removedLinks]);

  const removeLink = (url) => {
    setRemovedLinks(prev => new Set([...prev, url]));
    setDetectedLinks(prev => prev.filter(link => link.url !== url));
  };

  const resetRemovedLinks = () => {
    setRemovedLinks(new Set());
  };

  return {
    detectedLinks,
    loading,
    removeLink,
    resetRemovedLinks
  };
};

// Utilitaire pour détecter les URLs dans du texte (côté client)
export const detectUrlsInText = (text) => {
  const urlRegex = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)/g;
  return text.match(urlRegex) || [];
};

// Hook pour prévisualiser un lien unique
export const useLinkPreview = (url) => {
  const [linkData, setLinkData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!url) {
      setLinkData(null);
      setError(null);
      return;
    }

    const fetchLinkPreview = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await axios.post(`${API_BASE}/api/links/preview`, {
          url: url
        });

        setLinkData(response.data.metadata);
      } catch (err) {
        console.error('Error fetching link preview:', err);
        setError(err.response?.data?.detail || 'Erreur lors de la récupération de l\'aperçu');
        setLinkData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchLinkPreview();
  }, [url]);

  return { linkData, loading, error };
};