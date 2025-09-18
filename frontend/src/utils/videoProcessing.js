// Utilitaires pour le traitement vidéo côté client
// Compression, conversion et validation des vidéos

/**
 * Compresse une vidéo pour respecter les limites de taille
 * @param {File} videoFile - Fichier vidéo original
 * @param {number} maxSizeBytes - Taille maximale en bytes
 * @param {function} onProgress - Callback pour le progrès
 * @returns {Promise<Blob>} - Vidéo compressée
 */
export const compressVideo = async (videoFile, maxSizeBytes, onProgress = null) => {
  return new Promise((resolve, reject) => {
    try {
      const video = document.createElement('video');
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      video.onloadeddata = () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Calculer le ratio de compression nécessaire
        const compressionRatio = Math.sqrt(maxSizeBytes / videoFile.size);
        const targetWidth = Math.floor(video.videoWidth * compressionRatio);
        const targetHeight = Math.floor(video.videoHeight * compressionRatio);
        
        canvas.width = targetWidth;
        canvas.height = targetHeight;
        
        // Configuration MediaRecorder pour la compression
        const stream = canvas.captureStream(30); // 30 FPS
        const mediaRecorder = new MediaRecorder(stream, {
          videoBitsPerSecond: calculateBitrate(maxSizeBytes, video.duration)
        });
        
        const chunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
          chunks.push(event.data);
        };
        
        mediaRecorder.onstop = () => {
          const compressedBlob = new Blob(chunks, { type: 'video/mp4' });
          resolve(compressedBlob);
        };
        
        mediaRecorder.onerror = (error) => {
          reject(new Error(`Erreur compression: ${error.message}`));
        };
        
        // Démarrer l'enregistrement
        mediaRecorder.start();
        
        // Dessiner les frames de la vidéo sur le canvas
        const drawFrame = () => {
          if (video.currentTime < video.duration) {
            ctx.drawImage(video, 0, 0, targetWidth, targetHeight);
            
            if (onProgress) {
              const progress = (video.currentTime / video.duration) * 100;
              onProgress(progress);
            }
            
            video.currentTime += 1/30; // Avancer d'une frame
            requestAnimationFrame(drawFrame);
          } else {
            mediaRecorder.stop();
          }
        };
        
        video.currentTime = 0;
        drawFrame();
      };
      
      video.onerror = () => {
        reject(new Error('Erreur chargement vidéo pour compression'));
      };
      
      video.src = URL.createObjectURL(videoFile);
    } catch (error) {
      reject(new Error(`Erreur compression vidéo: ${error.message}`));
    }
  });
};

/**
 * Calcule le bitrate optimal pour une taille cible
 * @param {number} targetSizeBytes - Taille cible en bytes
 * @param {number} durationSeconds - Durée en secondes
 * @returns {number} - Bitrate en bits par seconde
 */
const calculateBitrate = (targetSizeBytes, durationSeconds) => {
  // Réserver 10% pour l'audio et les métadonnées
  const videoBudget = targetSizeBytes * 0.9;
  const bitrate = (videoBudget * 8) / durationSeconds; // bits par seconde
  
  // Limiter le bitrate pour éviter une qualité trop dégradée
  const minBitrate = 500000; // 500 kbps minimum
  const maxBitrate = 5000000; // 5 Mbps maximum
  
  return Math.max(minBitrate, Math.min(maxBitrate, bitrate));
};

/**
 * Découpe une vidéo à une durée maximale
 * @param {File} videoFile - Fichier vidéo original
 * @param {number} maxDurationSeconds - Durée maximale en secondes
 * @param {function} onProgress - Callback pour le progrès
 * @returns {Promise<Blob>} - Vidéo découpée
 */
export const trimVideo = async (videoFile, maxDurationSeconds, onProgress = null) => {
  return new Promise((resolve, reject) => {
    try {
      const video = document.createElement('video');
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      video.onloadeddata = () => {
        if (video.duration <= maxDurationSeconds) {
          // Pas besoin de découper
          resolve(videoFile);
          return;
        }
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const stream = canvas.captureStream(30);
        const mediaRecorder = new MediaRecorder(stream, {
          videoBitsPerSecond: 2000000 // 2 Mbps pour une bonne qualité
        });
        
        const chunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
          chunks.push(event.data);
        };
        
        mediaRecorder.onstop = () => {
          const trimmedBlob = new Blob(chunks, { type: 'video/mp4' });
          resolve(trimmedBlob);
        };
        
        mediaRecorder.onerror = (error) => {
          reject(new Error(`Erreur découpage: ${error.message}`));
        };
        
        // Démarrer l'enregistrement
        mediaRecorder.start();
        
        // Dessiner les frames jusqu'à la durée maximale
        const drawFrame = () => {
          if (video.currentTime < maxDurationSeconds) {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            if (onProgress) {
              const progress = (video.currentTime / maxDurationSeconds) * 100;
              onProgress(progress);
            }
            
            video.currentTime += 1/30;
            requestAnimationFrame(drawFrame);
          } else {
            mediaRecorder.stop();
          }
        };
        
        video.currentTime = 0;
        drawFrame();
      };
      
      video.onerror = () => {
        reject(new Error('Erreur chargement vidéo pour découpage'));
      };
      
      video.src = URL.createObjectURL(videoFile);
    } catch (error) {
      reject(new Error(`Erreur découpage vidéo: ${error.message}`));
    }
  });
};

/**
 * Convertit une vidéo vers le format MP4
 * @param {File} videoFile - Fichier vidéo original
 * @param {function} onProgress - Callback pour le progrès
 * @returns {Promise<Blob>} - Vidéo convertie en MP4
 */
export const convertToMP4 = async (videoFile, onProgress = null) => {
  return new Promise((resolve, reject) => {
    try {
      // Si c'est déjà du MP4, pas besoin de convertir
      if (videoFile.type === 'video/mp4') {
        resolve(videoFile);
        return;
      }
      
      const video = document.createElement('video');
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      video.onloadeddata = () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const stream = canvas.captureStream(30);
        const mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'video/mp4',
          videoBitsPerSecond: 2000000
        });
        
        const chunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
          chunks.push(event.data);
        };
        
        mediaRecorder.onstop = () => {
          const mp4Blob = new Blob(chunks, { type: 'video/mp4' });
          resolve(mp4Blob);
        };
        
        mediaRecorder.onerror = (error) => {
          reject(new Error(`Erreur conversion: ${error.message}`));
        };
        
        // Démarrer l'enregistrement
        mediaRecorder.start();
        
        // Dessiner toutes les frames
        const drawFrame = () => {
          if (video.currentTime < video.duration) {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            if (onProgress) {
              const progress = (video.currentTime / video.duration) * 100;
              onProgress(progress);
            }
            
            video.currentTime += 1/30;
            requestAnimationFrame(drawFrame);
          } else {
            mediaRecorder.stop();
          }
        };
        
        video.currentTime = 0;
        drawFrame();
      };
      
      video.onerror = () => {
        reject(new Error('Erreur chargement vidéo pour conversion'));
      };
      
      video.src = URL.createObjectURL(videoFile);
    } catch (error) {
      reject(new Error(`Erreur conversion vidéo: ${error.message}`));
    }
  });
};

/**
 * Traite automatiquement une vidéo selon les contraintes des plateformes
 * @param {File} videoFile - Fichier vidéo original
 * @param {Array} platforms - Plateformes cibles (['facebook', 'instagram'])
 * @param {function} onProgress - Callback pour le progrès
 * @returns {Promise<Object>} - Résultat du traitement
 */
export const processVideoForPlatforms = async (videoFile, platforms, onProgress = null) => {
  try {
    let processedVideo = videoFile;
    const processSteps = [];
    
    // Déterminer les contraintes les plus restrictives
    const needsInstagram = platforms.includes('instagram');
    const maxSize = needsInstagram ? 1024 * 1024 * 1024 : 10 * 1024 * 1024 * 1024; // 1GB pour Instagram, 10GB pour Facebook
    const maxDuration = needsInstagram ? 60 : 15 * 60; // 60s pour Instagram, 15min pour Facebook
    
    // Étape 1: Conversion vers MP4 si nécessaire
    if (videoFile.type !== 'video/mp4') {
      processSteps.push('Conversion vers MP4...');
      onProgress && onProgress({ step: 'conversion', progress: 0 });
      
      processedVideo = await convertToMP4(processedVideo, (progress) => {
        onProgress && onProgress({ step: 'conversion', progress });
      });
    }
    
    // Étape 2: Découpage si nécessaire
    const video = document.createElement('video');
    const videoDuration = await new Promise((resolve, reject) => {
      video.onloadeddata = () => resolve(video.duration);
      video.onerror = () => reject(new Error('Erreur analyse durée vidéo'));
      video.src = URL.createObjectURL(processedVideo);
    });
    
    if (videoDuration > maxDuration) {
      processSteps.push(`Découpage à ${maxDuration}s...`);
      onProgress && onProgress({ step: 'trimming', progress: 0 });
      
      processedVideo = await trimVideo(processedVideo, maxDuration, (progress) => {
        onProgress && onProgress({ step: 'trimming', progress });
      });
    }
    
    // Étape 3: Compression si nécessaire
    if (processedVideo.size > maxSize) {
      processSteps.push('Compression...');
      onProgress && onProgress({ step: 'compression', progress: 0 });
      
      processedVideo = await compressVideo(processedVideo, maxSize, (progress) => {
        onProgress && onProgress({ step: 'compression', progress });
      });
    }
    
    // Libérer les ressources
    URL.revokeObjectURL(video.src);
    
    return {
      success: true,
      processedVideo,
      originalSize: videoFile.size,
      finalSize: processedVideo.size,
      compressionRatio: processedVideo.size / videoFile.size,
      processSteps,
      platforms
    };
    
  } catch (error) {
    return {
      success: false,
      error: error.message,
      originalSize: videoFile.size
    };
  }
};

/**
 * Génère une miniature à partir d'une vidéo
 * @param {File|Blob} videoFile - Fichier vidéo
 * @param {number} timeOffset - Temps en secondes pour la capture
 * @returns {Promise<string>} - URL de la miniature (data URL)
 */
export const generateVideoThumbnail = async (videoFile, timeOffset = 1) => {
  return new Promise((resolve, reject) => {
    try {
      const video = document.createElement('video');
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      video.onloadeddata = () => {
        video.currentTime = Math.min(timeOffset, video.duration - 0.1);
      };
      
      video.onseeked = () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        const thumbnailDataURL = canvas.toDataURL('image/jpeg', 0.8);
        resolve(thumbnailDataURL);
      };
      
      video.onerror = () => {
        reject(new Error('Erreur génération miniature'));
      };
      
      video.src = URL.createObjectURL(videoFile);
    } catch (error) {
      reject(new Error(`Erreur génération miniature: ${error.message}`));
    }
  });
};

/**
 * Obtient les métadonnées d'une vidéo
 * @param {File|Blob} videoFile - Fichier vidéo
 * @returns {Promise<Object>} - Métadonnées de la vidéo
 */
export const getVideoMetadata = async (videoFile) => {
  return new Promise((resolve, reject) => {
    try {
      const video = document.createElement('video');
      
      video.onloadeddata = () => {
        const metadata = {
          duration: video.duration,
          width: video.videoWidth,
          height: video.videoHeight,
          aspectRatio: video.videoWidth / video.videoHeight,
          size: videoFile.size,
          type: videoFile.type || 'video/mp4'
        };
        
        resolve(metadata);
      };
      
      video.onerror = () => {
        reject(new Error('Erreur lecture métadonnées vidéo'));
      };
      
      video.src = URL.createObjectURL(videoFile);
    } catch (error) {
      reject(new Error(`Erreur métadonnées vidéo: ${error.message}`));
    }
  });
};