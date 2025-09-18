import React, { useState, useRef } from 'react';
import { Upload, Video, Play, Pause, Volume2, VolumeX, X, FileVideo, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import axios from 'axios';
import { handleAxiosError } from '../utils/errorHandler';
import { processVideoForPlatforms, generateVideoThumbnail } from '../utils/videoProcessing';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const VideoUploader = ({ onVideoUploaded, onError, disabled = false, platforms = ['facebook', 'instagram'] }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [processedVideo, setProcessedVideo] = useState(null);
  const [videoPreview, setVideoPreview] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(true);
  const [validationResult, setValidationResult] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState('');
  const [processingProgress, setProcessingProgress] = useState(0);
  const [needsProcessing, setNeedsProcessing] = useState(false);
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  // Supported video formats
  const supportedFormats = ['video/mp4', 'video/quicktime', 'video/avi', 'video/wmv', 'video/mov'];
  const maxFileSize = 1024 * 1024 * 1024; // 1GB for Instagram compatibility

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (disabled) return;
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = async (file) => {
    if (!file) return;

    // Basic validation
    const validation = validateVideoFile(file);
    setValidationResult(validation);

    if (!validation.valid) {
      onError && onError(validation.error);
      return;
    }

    setSelectedVideo(file);
    
    // Create video preview
    const videoUrl = URL.createObjectURL(file);
    setVideoPreview(videoUrl);

    // Get video metadata
    const video = document.createElement('video');
    video.src = videoUrl;
    video.onloadedmetadata = () => {
      const metadata = {
        duration: video.duration,
        width: video.videoWidth,
        height: video.videoHeight,
        size: file.size,
        type: file.type
      };
      
      // Enhanced validation with video metadata
      const enhancedValidation = validateVideoMetadata(metadata);
      setValidationResult({...validation, ...enhancedValidation});
      
      if (!enhancedValidation.valid) {
        onError && onError(enhancedValidation.error);
      }
    };
  };

  const validateVideoFile = (file) => {
    // Check file type
    if (!supportedFormats.includes(file.type)) {
      return {
        valid: false,
        error: `Format non supporté. Formats acceptés: MP4, MOV, AVI, WMV`,
        needsConversion: !['video/mp4', 'video/quicktime'].includes(file.type)
      };
    }

    // Check file size
    if (file.size > maxFileSize) {
      return {
        valid: false,
        error: `Fichier trop volumineux (${(file.size / (1024*1024*1024)).toFixed(1)} GB). Taille maximale: 1 GB`,
        needsCompression: true
      };
    }

    return { valid: true };
  };

  const validateVideoMetadata = (metadata) => {
    const maxDurationInstagram = 60; // 60 seconds for Instagram
    const maxDurationFacebook = 15 * 60; // 15 minutes for Facebook

    if (metadata.duration > maxDurationFacebook) {
      return {
        valid: false,
        error: `Vidéo trop longue (${Math.round(metadata.duration)}s). Durée maximale: 15 minutes (Facebook), 60s (Instagram)`,
        needsTrimming: true
      };
    }

    if (metadata.duration > maxDurationInstagram) {
      return {
        valid: true,
        warning: `Vidéo compatible Facebook seulement (${Math.round(metadata.duration)}s). Pour Instagram: max 60s`
      };
    }

    return { valid: true };
  };

  const handleUpload = async () => {
    if (!selectedVideo || !validationResult?.valid) return;

    try {
      setUploading(true);
      setUploadProgress(0);

      const formData = new FormData();
      formData.append('video', selectedVideo);
      formData.append('filename', selectedVideo.name);

      const response = await axios.post(`${API_BASE}/api/videos/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        }
      });

      if (response.data.success) {
        onVideoUploaded && onVideoUploaded({
          ...response.data,
          localPreview: videoPreview,
          metadata: validationResult
        });
        
        // Reset form
        resetForm();
      } else {
        throw new Error(response.data.error || 'Erreur upload');
      }

    } catch (error) {
      console.error('Video upload error:', error);
      const errorMessage = handleAxiosError(error);
      onError && onError(errorMessage);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const resetForm = () => {
    setSelectedVideo(null);
    setVideoPreview(null);
    setValidationResult(null);
    setIsPlaying(false);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const togglePlayPause = () => {
    if (!videoRef.current) return;
    
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-4">
      {/* Upload Zone */}
      {!selectedVideo && (
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : disabled
              ? 'border-gray-200 bg-gray-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={(e) => e.target.files[0] && handleFileSelect(e.target.files[0])}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={disabled}
          />
          
          <div className="space-y-4">
            <div className="w-16 h-16 mx-auto bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <Video className="w-8 h-8 text-white" />
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-gray-800 mb-2">
                Glissez votre vidéo ici
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                ou cliquez pour sélectionner un fichier
              </p>
              
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={disabled}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Upload className="w-4 h-4 mr-2" />
                Sélectionner une vidéo
              </button>
            </div>
            
            <div className="text-xs text-gray-500 space-y-1">
              <p>Formats supportés: MP4, MOV, AVI, WMV</p>
              <p>Taille maximale: 1 GB</p>
              <p>Durée maximale: 60s (Instagram), 15min (Facebook)</p>
            </div>
          </div>
        </div>
      )}

      {/* Video Preview & Validation */}
      {selectedVideo && videoPreview && (
        <div className="space-y-4">
          {/* Video Player */}
          <div className="relative bg-black rounded-lg overflow-hidden">
            <video
              ref={videoRef}
              src={videoPreview}
              className="w-full max-h-96 object-contain"
              muted={isMuted}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onEnded={() => setIsPlaying(false)}
            />
            
            {/* Video Controls */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
              <div className="flex items-center justify-between text-white">
                <div className="flex items-center space-x-3">
                  <button
                    onClick={togglePlayPause}
                    className="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors"
                  >
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  </button>
                  
                  <button
                    onClick={toggleMute}
                    className="p-1 hover:bg-white/20 rounded transition-colors"
                  >
                    {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                  </button>
                </div>
                
                <button
                  onClick={resetForm}
                  className="p-1 hover:bg-white/20 rounded transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Video Information */}
          <div className="bg-gray-50 rounded-lg p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileVideo className="w-5 h-5 text-gray-600" />
                <span className="font-medium text-gray-800">{selectedVideo.name}</span>
              </div>
              <span className="text-sm text-gray-600">{formatFileSize(selectedVideo.size)}</span>
            </div>
            
            {validationResult && videoRef.current && (
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Durée:</span>
                  <span className="ml-1 font-medium">{formatDuration(videoRef.current.duration || 0)}</span>
                </div>
                <div>
                  <span className="text-gray-600">Résolution:</span>
                  <span className="ml-1 font-medium">
                    {videoRef.current.videoWidth}x{videoRef.current.videoHeight}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Format:</span>
                  <span className="ml-1 font-medium">{selectedVideo.type.split('/')[1].toUpperCase()}</span>
                </div>
              </div>
            )}
          </div>

          {/* Validation Status */}
          {validationResult && (
            <div className={`p-4 rounded-lg border ${
              validationResult.valid
                ? validationResult.warning
                  ? 'bg-yellow-50 border-yellow-200'
                  : 'bg-green-50 border-green-200'
                : 'bg-red-50 border-red-200'
            }`}>
              <div className="flex items-start space-x-2">
                {validationResult.valid ? (
                  validationResult.warning ? (
                    <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                  ) : (
                    <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                  )
                ) : (
                  <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
                )}
                
                <div className="flex-1">
                  <p className={`font-medium ${
                    validationResult.valid
                      ? validationResult.warning
                        ? 'text-yellow-800'
                        : 'text-green-800'
                      : 'text-red-800'
                  }`}>
                    {validationResult.valid
                      ? validationResult.warning
                        ? 'Avertissement'
                        : 'Vidéo compatible'
                      : 'Vidéo non compatible'
                    }
                  </p>
                  
                  <p className={`text-sm mt-1 ${
                    validationResult.valid
                      ? validationResult.warning
                        ? 'text-yellow-700'
                        : 'text-green-700'
                      : 'text-red-700'
                  }`}>
                    {validationResult.error || validationResult.warning || 'Votre vidéo respecte toutes les contraintes Meta'}
                  </p>
                  
                  {/* Suggestions for improvements */}
                  {(validationResult.needsConversion || validationResult.needsCompression || validationResult.needsTrimming) && (
                    <div className="mt-2 text-xs text-gray-600">
                      <p className="font-medium">Solutions automatiques disponibles :</p>
                      <ul className="mt-1 space-y-1">
                        {validationResult.needsConversion && (
                          <li>• Conversion automatique vers MP4</li>
                        )}
                        {validationResult.needsCompression && (
                          <li>• Compression pour respecter la limite de taille</li>
                        )}
                        {validationResult.needsTrimming && (
                          <li>• Découpage automatique pour Instagram (60s)</li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Upload Button */}
          <div className="flex justify-between items-center">
            <button
              onClick={resetForm}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Choisir une autre vidéo
            </button>
            
            <button
              onClick={handleUpload}
              disabled={!validationResult?.valid || uploading}
              className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? (
                <>
                  <Clock className="w-4 h-4 animate-spin" />
                  <span>Upload {uploadProgress}%</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Uploader la vidéo</span>
                </>
              )}
            </button>
          </div>

          {/* Progress Bar */}
          {uploading && (
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoUploader;