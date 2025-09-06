#!/usr/bin/env python3
"""
🚀 Script de démarrage pour FacebookPost
Backend + Frontend combinés sur FastAPI

Usage: python start_server.py [--port 8001]
"""

import argparse
import sys
import os
import uvicorn

# Ajouter le backend au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    parser = argparse.ArgumentParser(description='Démarrer le serveur FacebookPost')
    parser.add_argument('--port', type=int, default=8001, help='Port du serveur (défaut: 8001)')
    parser.add_argument('--host', default='0.0.0.0', help='Host du serveur (défaut: 0.0.0.0)')
    parser.add_argument('--no-ngrok', action='store_true', help='Désactiver ngrok')
    
    args = parser.parse_args()
    
    print("🚀 FacebookPost - Backend + Frontend combiné")
    print("=" * 50)
    print(f"📍 Serveur: http://{args.host}:{args.port}")
    print(f"🌐 Frontend React: http://{args.host}:{args.port}/")
    print(f"🔗 API Endpoints: http://{args.host}:{args.port}/api/*")
    print("✅ CORS: Activé pour toutes les origines")
    print("=" * 50)
    
    # Configuration optionnelle ngrok
    if args.no_ngrok:
        os.environ["ENABLE_NGROK"] = "false"
        print("🔧 Ngrok: Désactivé")
    else:
        print("🔧 Ngrok: Activé (si configuré)")
    
    print("")
    print("📋 Endpoints disponibles:")
    print("   GET  /              -> Frontend React")
    print("   GET  /static/*      -> Fichiers statiques (CSS, JS)")
    print("   GET  /api/health    -> Status serveur")
    print("   GET  /api/posts     -> Liste des posts")
    print("   POST /api/posts     -> Créer un post") 
    print("   POST /api/upload    -> Upload fichier")
    print("   GET  /api/webhook   -> Webhook Facebook (verification)")
    print("   POST /api/webhook   -> Webhook Facebook (events)")
    print("")
    
    try:
        # Import du serveur
        from server import app
        
        # Démarrage
        print("🎯 Démarrage en cours...")
        uvicorn.run(
            app, 
            host=args.host, 
            port=args.port,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Arrêt du serveur...")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()