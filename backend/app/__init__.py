"""
Flask application factory
"""

import os
from flask import Flask
from .utils.error_handlers import register_error_handlers
from .extensions import init_extensions

def create_app():
    """Create Flask application"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        UPLOAD_FOLDER=os.path.join(app.root_path, 'static', 'uploads'),
        RESULTS_FOLDER=os.path.join(app.root_path, 'static', 'results'),
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50MB max upload size
        CELERY_BROKER_URL=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        CELERY_RESULT_BACKEND=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        # CORS settings
        CORS_HEADERS='Content-Type',
        # Force HTTPS
        PREFERRED_URL_SCHEME='https'
    )
    
    # Ensure upload and results directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from .api import audio_routes, transcription_routes, sheet_music_routes
    
    app.register_blueprint(audio_routes.bp)
    app.register_blueprint(transcription_routes.bp)
    app.register_blueprint(sheet_music_routes.bp)
    
    # Add a simple route for testing
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'Music Transcription API is running'}
    
    return app