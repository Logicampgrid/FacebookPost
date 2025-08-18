import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Image, Video, X, Upload } from 'lucide-react';

const MediaUploader = ({ files, onFilesChange, disabled }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (disabled) return;
    
    const newFiles = [...files, ...acceptedFiles].slice(0, 4); // Limit to 4 files
    onFilesChange(newFiles);
  }, [files, onFilesChange, disabled]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
      'video/*': ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    },
    maxFiles: 4,
    maxSize: 100 * 1024 * 1024, // 100MB max per file
    disabled
  });

  const removeFile = (index) => {
    const newFiles = files.filter((_, i) => i !== index);
    onFilesChange(newFiles);
  };

  const getFileIcon = (file) => {
    if (file.type.startsWith('image/')) {
      return <Image className="w-4 h-4" />;
    } else if (file.type.startsWith('video/')) {
      return <Video className="w-4 h-4" />;
    }
    return <Upload className="w-4 h-4" />;
  };

  const getFilePreview = (file) => {
    const url = URL.createObjectURL(file);
    const fileSize = (file.size / (1024 * 1024)).toFixed(1); // Size in MB
    
    if (file.type.startsWith('image/')) {
      return (
        <div className="relative">
          <img 
            src={url} 
            alt="Preview" 
            className="w-full h-20 object-contain bg-gray-100 rounded"
            onLoad={() => URL.revokeObjectURL(url)}
          />
          <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-1 rounded-b">
            📸 {fileSize}MB
          </div>
        </div>
      );
    } else if (file.type.startsWith('video/')) {
      return (
        <div className="relative">
          <video 
            src={url} 
            className="w-full h-20 object-contain bg-gray-100 rounded"
            onLoadedData={() => URL.revokeObjectURL(url)}
            muted
          />
          <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center rounded">
            <Video className="w-6 h-6 text-white" />
          </div>
          <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-1 rounded-b">
            🎥 {fileSize}MB
          </div>
        </div>
      );
    }
    
    return (
      <div className="w-full h-20 bg-gray-100 rounded flex items-center justify-center flex-col">
        {getFileIcon(file)}
        <span className="text-xs text-gray-500 mt-1">{fileSize}MB</span>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="text-center">
          <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-600">
            {isDragActive ? 'Déposez les fichiers ici...' : 'Cliquez ou glissez des images/vidéos'}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Maximum 4 fichiers • PNG, JPG, GIF, WebP, MP4, MOV, AVI • Max 100MB par fichier
          </p>
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {files.map((file, index) => (
            <div key={index} className="relative group">
              <div className="border rounded-lg overflow-hidden">
                {getFilePreview(file)}
              </div>
              
              <button
                onClick={() => removeFile(index)}
                className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                disabled={disabled}
              >
                <X className="w-3 h-3" />
              </button>
              
              <div className="mt-1 text-xs text-gray-500 truncate">
                {file.name}
              </div>
            </div>
          ))}
        </div>
      )}

      {files.length >= 4 && (
        <p className="text-xs text-orange-500">
          Limite de 4 fichiers atteinte
        </p>
      )}
    </div>
  );
};

export default MediaUploader;