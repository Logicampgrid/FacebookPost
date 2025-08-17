import React, { useState, useEffect } from 'react';
import { Instagram, AlertCircle, CheckCircle, Play, RefreshCw } from 'lucide-react';
import axios from 'axios';

const InstagramDiagnostics = ({ API_BASE }) => {
  const [diagnosis, setDiagnosis] = useState(null);
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);

  const runDiagnosis = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/api/debug/instagram-complete-diagnosis`);
      setDiagnosis(response.data);
    } catch (error) {
      console.error('Diagnosis error:', error);
      setDiagnosis({
        status: 'error',
        error: 'Failed to run diagnosis'
      });
    } finally {
      setLoading(false);
    }
  };

  const testInstagramPublication = async () => {
    setTesting(true);
    try {
      const response = await axios.post(`${API_BASE}/api/debug/test-instagram-publication`);
      setTestResult(response.data);
    } catch (error) {
      console.error('Instagram test error:', error);
      setTestResult({
        success: false,
        error: 'Test request failed'
      });
    } finally {
      setTesting(false);
    }
  };

  useEffect(() => {
    runDiagnosis();
  }, []);

  const getStatusColor = (hasIssues) => {
    return hasIssues ? 'text-red-600' : 'text-green-600';
  };

  const getStatusIcon = (hasIssues) => {
    return hasIssues ? <AlertCircle className="w-5 h-5" /> : <CheckCircle className="w-5 h-5" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Instagram className="w-6 h-6 text-pink-600" />
          <h3 className="text-lg font-semibold text-gray-800">Instagram Publication Diagnostics</h3>
        </div>
        <button
          onClick={runDiagnosis}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center space-x-3 text-gray-600">
            <RefreshCw className="w-5 h-5 animate-spin" />
            <span>Running Instagram diagnosis...</span>
          </div>
        </div>
      )}

      {diagnosis && !loading && (
        <div className="space-y-6">
          {/* Authentication Status */}
          <div className="p-4 border border-gray-200 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">👤 Authentication Status</h4>
            <div className="space-y-2">
              <div className={`flex items-center space-x-2 ${getStatusColor(!diagnosis.authentication.user_found)}`}>
                {getStatusIcon(!diagnosis.authentication.user_found)}
                <span>
                  {diagnosis.authentication.user_found 
                    ? `✅ User authenticated: ${diagnosis.authentication.user_name}`
                    : '❌ No authenticated user found'
                  }
                </span>
              </div>
              
              {diagnosis.authentication.user_found && (
                <div className={`flex items-center space-x-2 ${getStatusColor(diagnosis.authentication.business_managers_count === 0)}`}>
                  {getStatusIcon(diagnosis.authentication.business_managers_count === 0)}
                  <span>
                    Business Managers: {diagnosis.authentication.business_managers_count}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Instagram Accounts */}
          <div className="p-4 border border-gray-200 rounded-lg">
            <h4 className="font-medium text-gray-800 mb-3">📱 Instagram Business Accounts</h4>
            {diagnosis.instagram_accounts.length === 0 ? (
              <div className="text-red-600 flex items-center space-x-2">
                <AlertCircle className="w-5 h-5" />
                <span>No Instagram Business accounts found</span>
              </div>
            ) : (
              <div className="space-y-3">
                {diagnosis.instagram_accounts.map((account, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Instagram className="w-5 h-5 text-pink-600" />
                      <div>
                        <div className="font-medium">@{account.username}</div>
                        <div className="text-sm text-gray-600">
                          {account.name} ({account.account_type})
                        </div>
                        <div className="text-xs text-gray-500">
                          Connected to: {account.connected_page}
                        </div>
                      </div>
                      <div className="ml-auto text-sm text-green-600">
                        {account.status}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Issues */}
          {diagnosis.issues.length > 0 && (
            <div className="p-4 border border-red-200 bg-red-50 rounded-lg">
              <h4 className="font-medium text-red-800 mb-3">❌ Issues Found</h4>
              <div className="space-y-2">
                {diagnosis.issues.map((issue, index) => (
                  <div key={index} className="text-red-700 text-sm">
                    • {issue}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {diagnosis.recommendations.length > 0 && (
            <div className="p-4 border border-blue-200 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-800 mb-3">💡 Recommendations</h4>
              <div className="space-y-2">
                {diagnosis.recommendations.map((rec, index) => (
                  <div key={index} className="text-blue-700 text-sm">
                    {rec}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Test Publication */}
          {diagnosis.instagram_accounts.length > 0 && (
            <div className="p-4 border border-green-200 bg-green-50 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-green-800">🧪 Test Instagram Publication</h4>
                <button
                  onClick={testInstagramPublication}
                  disabled={testing}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                >
                  <Play className={`w-4 h-4 ${testing ? 'hidden' : ''}`} />
                  <RefreshCw className={`w-4 h-4 ${testing ? 'animate-spin' : 'hidden'}`} />
                  <span>{testing ? 'Testing...' : 'Test Publication'}</span>
                </button>
              </div>
              <p className="text-green-700 text-sm mb-3">
                This will create a test post on Instagram to verify the publication system works.
              </p>
              
              {testResult && (
                <div className={`mt-3 p-3 rounded-lg ${testResult.success ? 'bg-green-100 border border-green-300' : 'bg-red-100 border border-red-300'}`}>
                  <div className={`font-medium ${testResult.success ? 'text-green-800' : 'text-red-800'}`}>
                    {testResult.success ? '✅ Test Successful!' : '❌ Test Failed'}
                  </div>
                  <div className={`text-sm mt-1 ${testResult.success ? 'text-green-700' : 'text-red-700'}`}>
                    {testResult.success 
                      ? `Posted to @${testResult.connected_page} (ID: ${testResult.instagram_post_id})`
                      : testResult.error
                    }
                  </div>
                  {testResult.success && testResult.method_used && (
                    <div className="text-xs text-green-600 mt-1">
                      Method: {testResult.method_used}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Quick Setup Guide */}
      <div className="p-4 border border-gray-200 rounded-lg">
        <h4 className="font-medium text-gray-800 mb-3">🚀 Quick Setup Guide</h4>
        <div className="space-y-2 text-sm text-gray-600">
          <div>1. 🔑 Login with Facebook Business Manager account</div>
          <div>2. 📱 Ensure Instagram Business accounts are connected to Facebook pages</div>
          <div>3. 🔒 Verify Instagram publishing permissions in Meta Business</div>
          <div>4. 🧪 Run the test publication above</div>
          <div>5. 🚀 Start publishing content to Instagram!</div>
        </div>
      </div>
    </div>
  );
};

export default InstagramDiagnostics;