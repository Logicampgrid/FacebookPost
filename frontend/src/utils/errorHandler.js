// Utility functions for handling API errors and validation errors
// Converts error objects to user-friendly strings

/**
 * Formats FastAPI/Pydantic validation error objects for display
 * @param {Object|Array|String} error - The error object/array/string from API
 * @returns {String} - Formatted error message
 */
export const formatErrorMessage = (error) => {
  // If it's already a string, return it
  if (typeof error === 'string') {
    return error;
  }
  
  // If it's null or undefined, return default message
  if (!error) {
    return 'Une erreur inconnue s\'est produite';
  }
  
  // Handle array of validation errors (common with FastAPI)
  if (Array.isArray(error)) {
    return error.map(formatSingleError).join('; ');
  }
  
  // Handle single validation error object
  if (typeof error === 'object') {
    return formatSingleError(error);
  }
  
  // Fallback - try to stringify
  try {
    return JSON.stringify(error);
  } catch (e) {
    return 'Erreur de format invalide';
  }
};

/**
 * Formats a single validation error object
 * @param {Object} errorObj - Single error object with type, loc, msg, etc.
 * @returns {String} - Formatted error message
 */
const formatSingleError = (errorObj) => {
  // If it has a msg property (Pydantic format), use it
  if (errorObj.msg) {
    // If there's location info, include it
    if (errorObj.loc && Array.isArray(errorObj.loc) && errorObj.loc.length > 0) {
      const fieldName = errorObj.loc[errorObj.loc.length - 1];
      return `${fieldName}: ${errorObj.msg}`;
    }
    return errorObj.msg;
  }
  
  // If it has a message property, use it
  if (errorObj.message) {
    return errorObj.message;
  }
  
  // If it has a detail property, use it
  if (errorObj.detail) {
    return typeof errorObj.detail === 'string' ? errorObj.detail : formatErrorMessage(errorObj.detail);
  }
  
  // If it has an error property, recursively format it
  if (errorObj.error) {
    return formatErrorMessage(errorObj.error);
  }
  
  // Try to extract meaningful information from the object
  const meaningfulKeys = ['type', 'loc', 'msg', 'input', 'url', 'message', 'detail'];
  const relevantInfo = {};
  
  meaningfulKeys.forEach(key => {
    if (errorObj[key] !== undefined) {
      relevantInfo[key] = errorObj[key];
    }
  });
  
  // If we found some relevant info, format it nicely
  if (Object.keys(relevantInfo).length > 0) {
    if (relevantInfo.msg) {
      return relevantInfo.msg;
    }
    
    // Create a readable summary
    let summary = '';
    if (relevantInfo.loc && Array.isArray(relevantInfo.loc)) {
      summary += `Champ ${relevantInfo.loc.join('.')}: `;
    }
    if (relevantInfo.type) {
      summary += `Erreur ${relevantInfo.type}`;
    }
    if (relevantInfo.msg) {
      summary += ` - ${relevantInfo.msg}`;
    }
    
    return summary || 'Erreur de validation';
  }
  
  // Last resort - stringify the object keys
  return `Erreur: ${Object.keys(errorObj).join(', ')}`;
};

/**
 * Extracts error message from Axios error response
 * @param {Error} axiosError - Axios error object
 * @returns {String} - Formatted error message
 */
export const handleAxiosError = (axiosError) => {
  if (!axiosError) {
    return 'Erreur inconnue';
  }
  
  // Network error
  if (axiosError.code === 'NETWORK_ERROR' || !axiosError.response) {
    return 'Impossible de se connecter au serveur. Vérifiez votre connexion.';
  }
  
  // HTTP error with response
  if (axiosError.response) {
    const { status, data } = axiosError.response;
    
    // Handle different HTTP status codes
    switch (status) {
      case 400:
        return data?.detail ? formatErrorMessage(data.detail) : 'Requête invalide';
      case 401:
        return 'Non autorisé. Veuillez vous reconnecter.';
      case 403:
        return 'Accès refusé. Permissions insuffisantes.';
      case 404:
        return 'Ressource non trouvée';
      case 422:
        // Validation error - this is the main case we're fixing
        if (data?.detail) {
          return formatErrorMessage(data.detail);
        }
        return 'Erreur de validation des données';
      case 500:
        return 'Erreur serveur interne. Veuillez réessayer.';
      case 502:
        return 'Passerelle défaillante. Le serveur est temporairement indisponible.';
      case 503:
        return 'Service temporairement indisponible';
      default:
        // Try to extract error message from response
        if (data?.detail) {
          return formatErrorMessage(data.detail);
        }
        if (data?.message) {
          return formatErrorMessage(data.message);
        }
        return `Erreur HTTP ${status}`;
    }
  }
  
  // Other error types
  if (axiosError.message) {
    return axiosError.message;
  }
  
  return 'Erreur inconnue';
};

/**
 * Safe error display - ensures we never render objects directly
 * @param {any} error - Any error value
 * @returns {String} - Safe string for display
 */
export const safeErrorDisplay = (error) => {
  try {
    return formatErrorMessage(error);
  } catch (e) {
    console.error('Error formatting error message:', e);
    return 'Erreur de format';
  }
};

/**
 * Component helper for displaying errors safely
 * @param {any} error - Error to display
 * @returns {String} - Safe error string
 */
export const getDisplayError = (error) => {
  if (!error) return '';
  
  // Handle Axios errors
  if (error.isAxiosError || error.response || error.request) {
    return handleAxiosError(error);
  }
  
  // Handle other errors
  return safeErrorDisplay(error);
};