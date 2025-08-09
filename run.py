#!/usr/bin/env python3
"""
Development server runner for the Quran Learning API
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Set development environment
    os.environ["FLASK_ENV"] = "development"
    
    # Get port from environment or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    print(f"🚀 Starting Quran Learning API on port {port}")
    print(f"📖 API Documentation: http://localhost:{port}/api/v1/")
    print(f"🔧 Environment: {os.environ.get('FLASK_ENV', 'production')}")
    
    # Run the application
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    ) 