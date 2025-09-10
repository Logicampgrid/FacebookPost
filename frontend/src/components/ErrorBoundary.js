import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { safeErrorDisplay } from '../utils/errorHandler';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      retryCount: 0 
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // You can also log the error to an error reporting service here
    // errorReportingService.logError(error, errorInfo);
  }

  handleRetry = () => {
    this.setState(prevState => ({
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: prevState.retryCount + 1
    }));
  };

  render() {
    if (this.state.hasError) {
      // Fallback UI
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
            <div className="text-center">
              <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-800 mb-2">
                Oops! Une erreur s'est produite
              </h2>
              <p className="text-gray-600 mb-4">
                L'application a rencontré une erreur inattendue.
              </p>
              
              {/* Error Details */}
              <div className="text-left bg-gray-50 rounded-lg p-4 mb-4">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Détails de l'erreur :</h3>
                <div className="text-sm text-gray-600 space-y-1">
                  <div>
                    <span className="font-medium">Message:</span> 
                    <span className="ml-1">{safeErrorDisplay(this.state.error?.message)}</span>
                  </div>
                  {this.state.error?.name && (
                    <div>
                      <span className="font-medium">Type:</span> 
                      <span className="ml-1">{this.state.error.name}</span>
                    </div>
                  )}
                  {this.state.retryCount > 0 && (
                    <div>
                      <span className="font-medium">Tentatives:</span> 
                      <span className="ml-1">{this.state.retryCount}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2">
                <button
                  onClick={this.handleRetry}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Réessayer</span>
                </button>
                
                <button
                  onClick={() => window.location.reload()}
                  className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Recharger la page
                </button>
              </div>

              {/* Development Details (only in development) */}
              {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                <details className="mt-4 text-left">
                  <summary className="text-sm font-medium text-gray-700 cursor-pointer">
                    Détails techniques (développement)
                  </summary>
                  <div className="mt-2 text-xs text-gray-500 bg-gray-100 rounded p-2 overflow-auto max-h-32">
                    <div className="mb-2">
                      <strong>Stack trace:</strong>
                      <pre className="whitespace-pre-wrap">{this.state.error?.stack}</pre>
                    </div>
                    <div>
                      <strong>Component stack:</strong>
                      <pre className="whitespace-pre-wrap">{this.state.errorInfo?.componentStack}</pre>
                    </div>
                  </div>
                </details>
              )}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;