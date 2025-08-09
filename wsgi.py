#!/usr/bin/env python3
"""
WSGI entry point for the Quran Learning API
"""
import os
from app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # Get port from environment or default to 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Run the application
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("FLASK_ENV") == "development"
    ) 