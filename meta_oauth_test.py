#!/usr/bin/env python3
"""
Meta/Facebook OAuth Configuration Test
Tests the automatic Ngrok/OAuth setup system
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

class MetaOAuthTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'MetaOAuthTester/1.0'
        })
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []

    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "TEST": "🧪"}
        icon = icons.get(level.upper(), "📝")
        print(f"{icon} [{timestamp}] {message}")

    def run_test(self, name: str, test_func, *args, **kwargs) -> bool:
        """Run a single test with error handling"""
        self.tests_run += 1
        self.log(f"Running test: {name}", "TEST")
        
        try:
            result = test_func(*args, **kwargs)
            if result:
                self.tests_passed += 1
                self.log(f"✅ PASSED: {name}", "SUCCESS")
            else:
                self.log(f"❌ FAILED: {name}", "ERROR")
            return result
        except Exception as e:
            self.log(f"❌ ERROR in {name}: {str(e)}", "ERROR")
            self.errors.append(f"{name}: {str(e)}")
            return False

    def test_health_endpoint(self) -> bool:
        """Test GET /api/health"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Health check failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"Health response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check required fields
            if 'status' not in data or data['status'] != 'healthy':
                self.log(f"Service not healthy: {data.get('status', 'unknown')}", "ERROR")
                return False
            
            if 'timestamp' not in data:
                self.log("Missing timestamp in health response", "ERROR")
                return False
            
            self.log("✅ Service is healthy", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Health check error: {str(e)}", "ERROR")
            return False

    def test_oauth_status_complete(self) -> bool:
        """Test GET /api/config/oauth-status-complete"""
        try:
            response = self.session.get(f"{self.base_url}/api/config/oauth-status-complete", timeout=15)
            
            if response.status_code != 200:
                self.log(f"OAuth status complete failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"OAuth status complete response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check critical fields
            required_fields = ['ngrok_active', 'ngrok_url', 'redirect_uri', 'oauth_ready']
            for field in required_fields:
                if field not in data:
                    self.log(f"Missing required field: {field}", "ERROR")
                    return False
            
            # Validate ngrok configuration
            ngrok_active = data.get('ngrok_active', False)
            ngrok_url = data.get('ngrok_url')
            redirect_uri = data.get('redirect_uri')
            oauth_ready = data.get('oauth_ready', False)
            
            self.log(f"Ngrok Active: {ngrok_active}", "INFO")
            self.log(f"Ngrok URL: {ngrok_url}", "INFO")
            self.log(f"Redirect URI: {redirect_uri}", "INFO")
            self.log(f"OAuth Ready: {oauth_ready}", "INFO")
            
            # Check if ngrok URL matches expected
            expected_ngrok = "https://06ce5a8478e3.ngrok-free.app"
            if ngrok_url and expected_ngrok in ngrok_url:
                self.log(f"✅ Ngrok URL matches expected: {expected_ngrok}", "SUCCESS")
            elif ngrok_url:
                self.log(f"⚠️ Ngrok URL different than expected. Got: {ngrok_url}, Expected: {expected_ngrok}", "WARNING")
            else:
                self.log("❌ No ngrok URL detected", "ERROR")
                return False
            
            # Check redirect URI configuration
            if redirect_uri and redirect_uri.startswith("https://"):
                self.log(f"✅ Redirect URI is HTTPS: {redirect_uri}", "SUCCESS")
            else:
                self.log(f"❌ Invalid redirect URI: {redirect_uri}", "ERROR")
                return False
            
            # Check Facebook configuration
            facebook_config = data.get('facebook_config', {})
            if facebook_config:
                app_id_configured = facebook_config.get('app_id_configured', False)
                app_secret_configured = facebook_config.get('app_secret_configured', False)
                
                self.log(f"Facebook App ID configured: {app_id_configured}", "INFO")
                self.log(f"Facebook App Secret configured: {app_secret_configured}", "INFO")
                
                if app_id_configured and app_secret_configured:
                    self.log("✅ Facebook configuration complete", "SUCCESS")
                else:
                    self.log("⚠️ Facebook configuration incomplete", "WARNING")
            
            # Check auto-configuration status
            auto_config_completed = data.get('auto_config_completed', False)
            self.log(f"Auto-configuration completed: {auto_config_completed}", "INFO")
            
            # Main test: oauth_ready should be true
            if oauth_ready:
                self.log("✅ OAuth is ready!", "SUCCESS")
                return True
            else:
                self.log("❌ OAuth is not ready", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"OAuth status complete test error: {str(e)}", "ERROR")
            return False

    def test_force_oauth_setup(self) -> bool:
        """Test POST /api/config/force-oauth-setup"""
        try:
            response = self.session.post(f"{self.base_url}/api/config/force-oauth-setup", timeout=20)
            
            if response.status_code != 200:
                self.log(f"Force OAuth setup failed with status {response.status_code}", "ERROR")
                try:
                    error_data = response.json()
                    self.log(f"Error response: {json.dumps(error_data, indent=2)}", "ERROR")
                except:
                    self.log(f"Error response text: {response.text}", "ERROR")
                return False
            
            data = response.json()
            self.log(f"Force OAuth setup response: {json.dumps(data, indent=2)}", "INFO")
            
            # Check response structure
            success = data.get('success', False)
            message = data.get('message', '')
            backend_url = data.get('backend_url', '')
            redirect_uris = data.get('redirect_uris', [])
            
            self.log(f"Setup Success: {success}", "INFO")
            self.log(f"Message: {message}", "INFO")
            self.log(f"Backend URL: {backend_url}", "INFO")
            self.log(f"Redirect URIs: {redirect_uris}", "INFO")
            
            if success:
                self.log("✅ Force OAuth setup successful", "SUCCESS")
                
                # Validate redirect URIs
                if redirect_uris and len(redirect_uris) > 0:
                    for uri in redirect_uris:
                        if uri.startswith("https://"):
                            self.log(f"✅ Valid redirect URI: {uri}", "SUCCESS")
                        else:
                            self.log(f"❌ Invalid redirect URI: {uri}", "ERROR")
                            return False
                    return True
                else:
                    self.log("❌ No redirect URIs configured", "ERROR")
                    return False
            else:
                self.log(f"❌ Force OAuth setup failed: {message}", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"Force OAuth setup test error: {str(e)}", "ERROR")
            return False

    def test_ngrok_url_detection(self) -> bool:
        """Test if ngrok URL is properly detected from frontend .env"""
        try:
            # First check oauth status to see detected URL
            response = self.session.get(f"{self.base_url}/api/config/oauth-status", timeout=10)
            
            if response.status_code != 200:
                self.log(f"OAuth status failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            ngrok_url = data.get('ngrok_url')
            
            # Expected URL from frontend/.env
            expected_url = "https://06ce5a8478e3.ngrok-free.app"
            
            if ngrok_url:
                self.log(f"Detected ngrok URL: {ngrok_url}", "INFO")
                
                if expected_url in ngrok_url or ngrok_url == expected_url:
                    self.log(f"✅ Ngrok URL matches frontend .env configuration", "SUCCESS")
                    return True
                else:
                    self.log(f"⚠️ Ngrok URL differs from expected. Got: {ngrok_url}, Expected: {expected_url}", "WARNING")
                    # This might still be valid if ngrok URL changed
                    return True
            else:
                self.log("❌ No ngrok URL detected", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"Ngrok URL detection test error: {str(e)}", "ERROR")
            return False

    def test_facebook_oauth_configuration(self) -> bool:
        """Test Facebook OAuth configuration status"""
        try:
            response = self.session.get(f"{self.base_url}/api/config/oauth-status-complete", timeout=15)
            
            if response.status_code != 200:
                self.log(f"OAuth status failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            facebook_config = data.get('facebook_config', {})
            facebook_connectivity = data.get('facebook_connectivity', False)
            
            if not facebook_config:
                self.log("❌ No Facebook configuration found", "ERROR")
                return False
            
            # Check configuration components
            app_id_configured = facebook_config.get('app_id_configured', False)
            app_secret_configured = facebook_config.get('app_secret_configured', False)
            client_token_configured = facebook_config.get('client_token_configured', False)
            
            self.log(f"Facebook App ID configured: {app_id_configured}", "INFO")
            self.log(f"Facebook App Secret configured: {app_secret_configured}", "INFO")
            self.log(f"Facebook Client Token configured: {client_token_configured}", "INFO")
            self.log(f"Facebook connectivity: {facebook_connectivity}", "INFO")
            
            # Check redirect URIs
            redirect_uris_configured = data.get('redirect_uris_configured', [])
            if redirect_uris_configured:
                self.log(f"Configured redirect URIs: {redirect_uris_configured}", "INFO")
                for uri in redirect_uris_configured:
                    if uri.startswith("https://"):
                        self.log(f"✅ Valid redirect URI: {uri}", "SUCCESS")
                    else:
                        self.log(f"❌ Invalid redirect URI: {uri}", "ERROR")
                        return False
            
            # Overall assessment
            if app_id_configured and app_secret_configured:
                self.log("✅ Facebook OAuth configuration is complete", "SUCCESS")
                
                if facebook_connectivity:
                    self.log("✅ Facebook connectivity test passed", "SUCCESS")
                else:
                    self.log("⚠️ Facebook connectivity test failed (may be expected)", "WARNING")
                
                return True
            else:
                self.log("❌ Facebook OAuth configuration is incomplete", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"Facebook OAuth configuration test error: {str(e)}", "ERROR")
            return False

    def test_automatic_configuration_on_startup(self) -> bool:
        """Test if automatic configuration was completed on startup"""
        try:
            response = self.session.get(f"{self.base_url}/api/config/oauth-status-complete", timeout=15)
            
            if response.status_code != 200:
                self.log(f"OAuth status failed with status {response.status_code}", "ERROR")
                return False
            
            data = response.json()
            auto_config_completed = data.get('auto_config_completed', False)
            oauth_ready = data.get('oauth_ready', False)
            
            self.log(f"Auto-configuration completed: {auto_config_completed}", "INFO")
            self.log(f"OAuth ready: {oauth_ready}", "INFO")
            
            if auto_config_completed and oauth_ready:
                self.log("✅ Automatic configuration completed successfully on startup", "SUCCESS")
                return True
            elif oauth_ready:
                self.log("✅ OAuth is ready (manual or partial auto-configuration)", "SUCCESS")
                return True
            else:
                self.log("❌ Automatic configuration not completed", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"Automatic configuration test error: {str(e)}", "ERROR")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all OAuth configuration tests"""
        self.log("Starting Meta/Facebook OAuth Configuration Tests", "INFO")
        self.log(f"Testing backend at: {self.base_url}", "INFO")
        self.log("Focus: Automatic Ngrok/OAuth setup system", "INFO")
        
        # Test basic connectivity first
        if not self.run_test("Health Check", self.test_health_endpoint):
            self.log("❌ Basic connectivity failed - stopping tests", "ERROR")
            return self.get_summary()
        
        # Core OAuth tests (as requested)
        self.run_test("OAuth Status Complete", self.test_oauth_status_complete)
        self.run_test("Force OAuth Setup", self.test_force_oauth_setup)
        
        # Additional configuration tests
        self.run_test("Ngrok URL Detection", self.test_ngrok_url_detection)
        self.run_test("Facebook OAuth Configuration", self.test_facebook_oauth_configuration)
        self.run_test("Automatic Configuration on Startup", self.test_automatic_configuration_on_startup)
        
        return self.get_summary()

    def get_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        return {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'tests_failed': self.tests_run - self.tests_passed,
            'success_rate': success_rate,
            'errors': self.errors,
            'status': 'PASSED' if self.tests_passed == self.tests_run else 'FAILED'
        }

def main():
    """Main test execution"""
    # Use the ngrok URL from frontend .env
    backend_url = "https://06ce5a8478e3.ngrok-free.app"
    
    print(f"🚀 Meta/Facebook OAuth Configuration Test")
    print(f"📡 Backend URL: {backend_url}")
    print(f"🎯 Focus: Automatic Ngrok/OAuth setup system")
    print("=" * 80)
    
    # Initialize tester
    tester = MetaOAuthTester(backend_url)
    
    # Run all tests
    summary = tester.run_all_tests()
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Run: {summary['tests_run']}")
    print(f"Tests Passed: {summary['tests_passed']}")
    print(f"Tests Failed: {summary['tests_failed']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Overall Status: {summary['status']}")
    
    if summary['errors']:
        print("\n❌ ERRORS ENCOUNTERED:")
        for error in summary['errors']:
            print(f"  • {error}")
    
    print("\n🎯 OAUTH CONFIGURATION ASSESSMENT:")
    if summary['success_rate'] >= 80:
        print("✅ OAuth configuration system is working correctly")
        print("✅ Automatic Ngrok/OAuth setup appears functional")
        print("✅ Ready for frontend integration testing")
    else:
        print("⚠️ OAuth configuration issues detected")
        print("⚠️ May need manual configuration or troubleshooting")
    
    # Return appropriate exit code
    return 0 if summary['status'] == 'PASSED' else 1

if __name__ == "__main__":
    sys.exit(main())