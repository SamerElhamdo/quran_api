from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_smorest import Api
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import json
from datetime import datetime
from typing import Dict, Any


# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
api = Api()
scheduler = BackgroundScheduler()


def init_extensions(app: Flask):
    """Initialize all Flask extensions."""
    
    # SQLAlchemy
    db.init_app(app)
    
    # Migrations
    migrate.init_app(app, db)
    
    # JWT
    jwt.init_app(app)
    
    # Rate Limiting
    limiter.init_app(app)
    
    # CORS
    CORS(app, origins=app.config["CORS_ORIGINS"])
    
    # API Documentation
    api.init_app(app)
    
    # Scheduler
    if not app.config.get("TESTING", False):
        scheduler.start()


def setup_logging(app: Flask):
    """Setup logging configuration."""
    
    if app.config["LOG_FORMAT"] == "json":
        # JSON logging for production
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }
                
                if hasattr(record, "request_id"):
                    log_entry["request_id"] = record.request_id
                
                if record.exc_info:
                    log_entry["exception"] = self.formatException(record.exc_info)
                
                return json.dumps(log_entry)
        
        formatter = JSONFormatter()
    else:
        # Text logging for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Setup handlers
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(app.config["LOG_LEVEL"])
    root_logger.addHandler(handler)
    
    # Configure Flask logger
    app.logger.setLevel(app.config["LOG_LEVEL"])
    app.logger.addHandler(handler)


def setup_rate_limiting(app: Flask):
    """Setup rate limiting rules."""
    
    # Note: Rate limiting will be applied to individual routes
    # rather than globally to avoid conflicts
    pass


def setup_scheduler(app: Flask):
    """Setup background scheduler for review queue generation."""
    
    if app.config.get("TESTING", False):
        return
    
    # Temporarily disabled scheduler setup
    # from app.review.services import generate_review_queue
    
    # Schedule daily review queue generation at 03:00
    # scheduler.add_job(
    #     func=generate_review_queue,
    #     trigger="cron",
    #     hour=3,
    #     minute=0,
    #     id="generate_review_queue",
    #     replace_existing=True,
    #     timezone=app.config["SCHEDULER_TIMEZONE"]
    # )
    
    app.logger.info("Scheduler setup temporarily disabled")


def create_request_id_middleware():
    """Create middleware to add request ID to all requests."""
    
    def middleware(app):
        @app.before_request
        def before_request():
            import uuid
            from flask import g, request
            
            # Generate unique request ID
            g.request_id = str(uuid.uuid4())
            
            # Add request ID to logger context
            if hasattr(logging, "getLogger"):
                logger = logging.getLogger(__name__)
                logger = logging.LoggerAdapter(logger, {"request_id": g.request_id})
                g.logger = logger
            
            # Log request
            app.logger.info(
                f"Request started",
                extra={
                    "request_id": g.request_id,
                    "method": request.method,
                    "path": request.path,
                    "ip": get_remote_address(),
                }
            )
        
        @app.after_request
        def after_request(response):
            from flask import g
            
            # Log response
            if hasattr(g, "request_id"):
                app.logger.info(
                    f"Request completed",
                    extra={
                        "request_id": g.request_id,
                        "status_code": response.status_code,
                        "content_length": response.content_length,
                    }
                )
            
            # Add request ID to response headers for debugging
            if hasattr(g, "request_id"):
                response.headers["X-Request-ID"] = g.request_id
            
            return response
        
        @app.teardown_appcontext
        def teardown_appcontext(exception):
            from flask import g
            
            # Clean up request context
            if hasattr(g, "request_id"):
                del g.request_id
            if hasattr(g, "logger"):
                del g.logger
    
    return middleware 