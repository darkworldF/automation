#!/usr/bin/env python3
"""
Local Development Server
Run this script to start the web application locally for testing
"""

import os
from app import app, socketio

if __name__ == '__main__':
    # Load environment variables from .env file if it exists
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
    
    # Set default environment variables for development
    os.environ.setdefault('SECRET_KEY', 'dev-secret-key-change-in-production')
    os.environ.setdefault('FLASK_ENV', 'development')
    
    print("\n" + "="*50)
    print("🚀 Starting Engwe Monitor Web Application")
    print("="*50)
    print("🌐 Local URL: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000")
    print("⚙️ Settings: http://localhost:5000/settings")
    print("\n🔑 Make sure to configure your Shopify API credentials in Settings!")
    print("\n🚫 Press Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    # Start the Flask-SocketIO development server
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=True,
        use_reloader=True
    )