#!/usr/bin/env python3
"""
Système de Monitoring et Tests Automatiques
Surveille la santé du système et effectue des tests périodiques
"""
import os
import sys
import asyncio
import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import traceback

@dataclass
class HealthCheck:
    """Résultat d'un test de santé"""
    component: str
    status: str  # "healthy", "warning", "error"
    message: str
    timestamp: datetime
    details: Optional[Dict] = None

class SystemMonitor:
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.checks_history: List[HealthCheck] = []
        self.max_history = 100
        
    def log_monitor(self, message: str, level: str = "INFO"):
        """Logging pour le monitoring"""
        icons = {"INFO": "🔍", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "HEALTH": "🏥"}
        icon = icons.get(level.upper(), "🔍")
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{icon} [{timestamp}] [MONITOR] {message}")
    
    def add_check_result(self, check: HealthCheck):
        """Ajouter un résultat de test à l'historique"""
        self.checks_history.append(check)
        if len(self.checks_history) > self.max_history:
            self.checks_history = self.checks_history[-self.max_history:]
    
    async def check_backend_health(self) -> HealthCheck:
        """Test de santé du backend"""
        try:
            self.log_monitor("Test de santé du backend...", "HEALTH")
            
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/api/test-gizmobbs", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                ngrok_available = data.get("ngrok", {}).get("url") is not None
                ftp_working = "✅" in data.get("ftp", {}).get("connection_test", "")
                
                details = {
                    "response_time_ms": round(response_time * 1000, 2),
                    "ngrok_available": ngrok_available,
                    "ftp_working": ftp_working,
                    "stores_configured": len(data.get("configuration", {}))
                }
                
                if response_time > 5:
                    status = "warning"
                    message = f"Backend lent ({details['response_time_ms']}ms)"
                elif not ftp_working:
                    status = "warning" 
                    message = "Backend OK mais FTP non disponible"
                else:
                    status = "healthy"
                    message = f"Backend optimal ({details['response_time_ms']}ms)"
                    
                return HealthCheck(
                    component="backend",
                    status=status,
                    message=message,
                    timestamp=datetime.now(),
                    details=details
                )
            else:
                return HealthCheck(
                    component="backend",
                    status="error",
                    message=f"Erreur HTTP {response.status_code}",
                    timestamp=datetime.now(),
                    details={"http_status": response.status_code}
                )
                
        except requests.exceptions.ConnectionError:
            return HealthCheck(
                component="backend",
                status="error",
                message="Backend non accessible",
                timestamp=datetime.now(),
                details={"error": "connection_refused"}
            )
        except Exception as e:
            return HealthCheck(
                component="backend",
                status="error",
                message=f"Erreur test backend: {str(e)}",
                timestamp=datetime.now(),
                details={"error": str(e)}
            )
    
    async def check_webhook_endpoint(self) -> HealthCheck:
        """Test de l'endpoint webhook"""
        try:
            self.log_monitor("Test endpoint webhook...", "HEALTH")
            
            # Test GET (Facebook verification)
            start_time = time.time()
            response = requests.get(
                f"{self.backend_url}/api/webhook",
                params={
                    "hub.mode": "subscribe",
                    "hub.verify_token": "test_token",
                    "hub.challenge": "test_challenge_123"
                },
                timeout=5
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return HealthCheck(
                    component="webhook",
                    status="healthy",
                    message=f"Endpoint webhook OK ({round(response_time * 1000, 2)}ms)",
                    timestamp=datetime.now(),
                    details={"response_time_ms": round(response_time * 1000, 2)}
                )
            else:
                return HealthCheck(
                    component="webhook",
                    status="error",
                    message=f"Webhook erreur HTTP {response.status_code}",
                    timestamp=datetime.now(),
                    details={"http_status": response.status_code}
                )
                
        except Exception as e:
            return HealthCheck(
                component="webhook",
                status="error",
                message=f"Erreur test webhook: {str(e)}",
                timestamp=datetime.now(),
                details={"error": str(e)}
            )
    
    async def check_ftp_connection(self) -> HealthCheck:
        """Test de connexion FTP"""
        try:
            self.log_monitor("Test connexion FTP...", "HEALTH")
            
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/api/test-ftp", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                ftp_success = data.get("diagnostic", {}).get("success", False)
                
                details = {
                    "response_time_ms": round(response_time * 1000, 2),
                    "host_reachable": data.get("diagnostic", {}).get("host_reachable", False),
                    "login_success": data.get("diagnostic", {}).get("login_success", False),
                    "directory_accessible": data.get("diagnostic", {}).get("directory_accessible", False)
                }
                
                if ftp_success:
                    return HealthCheck(
                        component="ftp",
                        status="healthy",
                        message="FTP entièrement fonctionnel",
                        timestamp=datetime.now(),
                        details=details
                    )
                elif details["host_reachable"]:
                    return HealthCheck(
                        component="ftp",
                        status="warning",
                        message="FTP partiellement accessible",
                        timestamp=datetime.now(),
                        details=details
                    )
                else:
                    return HealthCheck(
                        component="ftp",
                        status="error",
                        message="FTP inaccessible",
                        timestamp=datetime.now(),
                        details=details
                    )
            else:
                return HealthCheck(
                    component="ftp",
                    status="error",
                    message=f"Test FTP erreur HTTP {response.status_code}",
                    timestamp=datetime.now(),
                    details={"http_status": response.status_code}
                )
                
        except Exception as e:
            return HealthCheck(
                component="ftp",
                status="error",
                message=f"Erreur test FTP: {str(e)}",
                timestamp=datetime.now(),
                details={"error": str(e)}
            )
    
    async def check_ngrok_status(self) -> HealthCheck:
        """Test du statut ngrok"""
        try:
            self.log_monitor("Test statut ngrok...", "HEALTH")
            
            # Tenter de contacter l'API ngrok locale
            try:
                response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
                if response.status_code == 200:
                    tunnels = response.json().get("tunnels", [])
                    active_tunnels = len(tunnels)
                    
                    if active_tunnels > 0:
                        return HealthCheck(
                            component="ngrok",
                            status="healthy", 
                            message=f"Ngrok actif ({active_tunnels} tunnel(s))",
                            timestamp=datetime.now(),
                            details={"active_tunnels": active_tunnels, "tunnels": tunnels}
                        )
                    else:
                        return HealthCheck(
                            component="ngrok",
                            status="warning",
                            message="Ngrok démarré mais aucun tunnel",
                            timestamp=datetime.now(),
                            details={"active_tunnels": 0}
                        )
                else:
                    return HealthCheck(
                        component="ngrok",
                        status="error",
                        message=f"API ngrok erreur {response.status_code}",
                        timestamp=datetime.now(),
                        details={"http_status": response.status_code}
                    )
                    
            except requests.exceptions.ConnectionError:
                return HealthCheck(
                    component="ngrok",
                    status="error",
                    message="Ngrok non démarré ou API inaccessible",
                    timestamp=datetime.now(),
                    details={"error": "api_not_available"}
                )
                
        except Exception as e:
            return HealthCheck(
                component="ngrok",
                status="error",
                message=f"Erreur test ngrok: {str(e)}",
                timestamp=datetime.now(),
                details={"error": str(e)}
            )
    
    async def run_full_health_check(self) -> Dict:
        """Effectue tous les tests de santé"""
        self.log_monitor("🏥 Début check de santé complet...", "HEALTH")
        
        # Effectuer tous les tests en parallèle
        checks = await asyncio.gather(
            self.check_backend_health(),
            self.check_webhook_endpoint(),
            self.check_ftp_connection(),
            self.check_ngrok_status(),
            return_exceptions=True
        )
        
        # Traiter les résultats
        valid_checks = []
        for check in checks:
            if isinstance(check, HealthCheck):
                valid_checks.append(check)
                self.add_check_result(check)
                
                # Log du résultat
                if check.status == "healthy":
                    self.log_monitor(f"✅ {check.component}: {check.message}", "SUCCESS")
                elif check.status == "warning":
                    self.log_monitor(f"⚠️ {check.component}: {check.message}", "WARNING")
                else:
                    self.log_monitor(f"❌ {check.component}: {check.message}", "ERROR")
            else:
                self.log_monitor(f"❌ Erreur check: {str(check)}", "ERROR")
        
        # Résumé global
        healthy_count = sum(1 for c in valid_checks if c.status == "healthy")
        warning_count = sum(1 for c in valid_checks if c.status == "warning")
        error_count = sum(1 for c in valid_checks if c.status == "error")
        
        overall_status = "healthy" if error_count == 0 and warning_count == 0 else \
                        "warning" if error_count == 0 else "error"
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "checks": {
                "total": len(valid_checks),
                "healthy": healthy_count,
                "warnings": warning_count,
                "errors": error_count
            },
            "components": [
                {
                    "component": check.component,
                    "status": check.status,
                    "message": check.message,
                    "details": check.details
                } for check in valid_checks
            ]
        }
        
        self.log_monitor(f"🏥 Check terminé: {healthy_count}✅ {warning_count}⚠️ {error_count}❌", "HEALTH")
        return summary
    
    async def continuous_monitoring(self, interval: int = 300):
        """Surveillance continue avec intervalle"""
        self.log_monitor(f"🔄 Démarrage surveillance continue (intervalle: {interval}s)", "INFO")
        
        while True:
            try:
                await self.run_full_health_check()
                await asyncio.sleep(interval)
            except KeyboardInterrupt:
                self.log_monitor("🛑 Surveillance interrompue par l'utilisateur", "INFO")
                break
            except Exception as e:
                self.log_monitor(f"❌ Erreur surveillance: {str(e)}", "ERROR")
                await asyncio.sleep(60)  # Attendre 1 minute avant de retry
    
    def generate_health_report(self) -> Dict:
        """Génère un rapport de santé détaillé"""
        if not self.checks_history:
            return {"message": "Aucune donnée de santé disponible"}
        
        recent_checks = self.checks_history[-20:]  # 20 derniers checks
        
        # Analyse par composant
        components_analysis = {}
        for check in recent_checks:
            comp = check.component
            if comp not in components_analysis:
                components_analysis[comp] = {"healthy": 0, "warning": 0, "error": 0, "total": 0}
            
            components_analysis[comp][check.status] += 1
            components_analysis[comp]["total"] += 1
        
        # Calcul fiabilité
        for comp, stats in components_analysis.items():
            if stats["total"] > 0:
                stats["reliability_percent"] = round((stats["healthy"] / stats["total"]) * 100, 2)
        
        return {
            "generated_at": datetime.now().isoformat(),
            "total_checks": len(self.checks_history),
            "recent_checks_analyzed": len(recent_checks),
            "components_analysis": components_analysis,
            "latest_check": {
                "component": recent_checks[-1].component,
                "status": recent_checks[-1].status,
                "message": recent_checks[-1].message,
                "timestamp": recent_checks[-1].timestamp.isoformat()
            } if recent_checks else None
        }

# Instance globale
system_monitor = SystemMonitor()

async def main():
    """Fonction principale pour tests"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            # Test unique
            result = await system_monitor.run_full_health_check()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif sys.argv[1] == "monitor":
            # Surveillance continue
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
            await system_monitor.continuous_monitoring(interval)
        elif sys.argv[1] == "report":
            # Rapport de santé
            report = system_monitor.generate_health_report()
            print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("Usage:")
        print("  python system_monitor.py check     # Test unique")
        print("  python system_monitor.py monitor [interval]  # Surveillance continue") 
        print("  python system_monitor.py report    # Rapport de santé")

if __name__ == "__main__":
    asyncio.run(main())