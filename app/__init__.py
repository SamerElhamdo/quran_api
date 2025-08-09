from flask import Flask
from app.config import get_config
from app.extensions import init_extensions, setup_logging, setup_rate_limiting, setup_scheduler


def create_app(config_name=None):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = get_config()
    else:
        config_name = get_config().get(config_name, get_config())
    
    app.config.from_object(config_name)
    config_name.init_app(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Setup logging
    setup_logging(app)
    
    # Setup rate limiting
    setup_rate_limiting(app)
    
    # Setup scheduler
    setup_scheduler(app)
    
    # Register blueprints
    from app.auth import auth_bp
    from app.content import content_bp
    from app.playlists import playlists_bp
    from app.review import review_bp
    from app.stats import stats_bp
    from app.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(content_bp, url_prefix="/api/v1/content")
    app.register_blueprint(playlists_bp, url_prefix="/api/v1/playlists")
    app.register_blueprint(review_bp, url_prefix="/api/v1/review")
    app.register_blueprint(stats_bp, url_prefix="/api/v1/stats")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500
    
    return app 