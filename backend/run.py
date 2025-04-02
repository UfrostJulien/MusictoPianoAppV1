"""
Main application entry point for the Music Transcription App.
"""

import os
from app import create_app

app = create_app()

@app.route('/')
def index():
    """Root endpoint for health check"""
    return {
        'status': 'ok',
        'message': 'Music Transcription API is running',
        'endpoints': {
            'audio': '/api/audio',
            'transcription': '/api/transcription',
            'sheet_music': '/api/sheet-music'
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Removed adhoc SSL for Render deployment
    # This allows proper CORS handling and prevents fetch errors
    app.run(host="0.0.0.0", port=port, debug=True)
