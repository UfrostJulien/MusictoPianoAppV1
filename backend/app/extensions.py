"""
Flask extensions initialization
"""

from flask_cors import CORS

# Initialize CORS
cors = CORS()

# Try to import Celery, but make it optional
try:
    from celery import Celery
    # Initialize Celery
    celery = Celery()
except ImportError:
    # Create a dummy Celery class for environments without Celery
    class DummyCelery:
        def __init__(self):
            self.Task = type('Task', (), {})
            
        def conf(self):
            return self
            
        def update(self, *args, **kwargs):
            pass
    
    celery = DummyCelery()

def init_extensions(app):
    """Initialize Flask extensions"""
    
    # Initialize CORS - allow all routes with proper headers for preflight requests
    cors.init_app(app, resources={r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False
    }})
    
    # Only initialize Celery if it's the real implementation
    if not isinstance(celery, DummyCelery):
        # Initialize Celery
        celery.conf.update(
            broker_url=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
            result_backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
        )
        
        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery
