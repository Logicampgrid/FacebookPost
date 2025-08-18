import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

const ImageOrientationTest = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      setResult(null);
    }
  };

  const testImageOrientation = async () => {
    if (!selectedFile) return;
    
    try {
      setLoading(true);
      
      const formData = new FormData();
      formData.append('image', selectedFile);
      
      const response = await axios.post(
        `${API_BASE}/api/debug/test-image-orientation-fix`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      setResult(response.data);
    } catch (error) {
      console.error('Error testing image orientation:', error);
      setResult({
        success: false,
        error: error.response?.data?.detail || error.message
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="facebook-card p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        🖼️ Test de Correction d'Orientation des Images
      </h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sélectionner une image (de préférence verticale ou avec métadonnées EXIF) :
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="facebook-input"
          />
        </div>
        
        <button
          onClick={testImageOrientation}
          disabled={!selectedFile || loading}
          className="facebook-button disabled:opacity-50"
        >
          {loading ? '🔄 Test en cours...' : '🧪 Tester la Correction d\'Orientation'}
        </button>
        
        {result && (
          <div className={`p-4 rounded-lg border ${result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
            {result.success ? (
              <div>
                <h4 className="font-semibold text-green-800 mb-3">
                  ✅ {result.message}
                </h4>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Image originale */}
                  <div className="space-y-2">
                    <h5 className="font-medium text-gray-700">Image Originale:</h5>
                    <img
                      src={`${API_BASE}${result.original_image.url}`}
                      alt="Image originale"
                      className="w-full max-h-60 object-contain bg-gray-100 rounded border"
                    />
                    <p className="text-sm text-gray-600">
                      Taille: {(result.original_image.size_bytes / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  
                  {/* Image optimisée */}
                  <div className="space-y-2">
                    <h5 className="font-medium text-gray-700">Image Optimisée (avec correction EXIF):</h5>
                    <img
                      src={`${API_BASE}${result.optimized_image.url}`}
                      alt="Image optimisée"
                      className="w-full max-h-60 object-contain bg-gray-100 rounded border"
                    />
                    <p className="text-sm text-gray-600">
                      Taille: {(result.optimized_image.size_bytes / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
                
                <div className="mt-4 p-3 bg-blue-50 rounded border-l-4 border-blue-400">
                  <p className="text-sm text-blue-800">
                    <strong>Optimisation appliquée:</strong> {result.optimization_applied}
                  </p>
                  <p className="text-sm text-blue-700 mt-1">
                    {result.note}
                  </p>
                </div>
              </div>
            ) : (
              <div>
                <h4 className="font-semibold text-red-800 mb-2">
                  ❌ Échec du Test
                </h4>
                <p className="text-red-700">{result.error}</p>
              </div>
            )}
          </div>
        )}
      </div>
      
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium text-gray-800 mb-2">À propos de cette correction :</h4>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• ✅ Correction automatique de l'orientation EXIF</li>
          <li>• ✅ Support des rotations 90°, 180°, 270°</li>
          <li>• ✅ CSS `object-contain` au lieu d'`object-cover`</li>
          <li>• ✅ Préservation du ratio d'aspect original</li>
          <li>• ✅ Compatible avec toutes les plateformes (Facebook, Instagram)</li>
        </ul>
      </div>
    </div>
  );
};

export default ImageOrientationTest;