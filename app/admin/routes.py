from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, limiter
from app.models import User, Reciter, AyahIndex, Progress, Playlist
from app.schemas.common import PaginationSchema
from marshmallow import ValidationError
import math
from datetime import datetime
import psutil
from . import admin_bp


def admin_required(f):
    """Decorator to check if user is admin."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != "admin":
            return {"error": "Admin access required"}, 403
        
        return f(*args, **kwargs)
    
    return decorated_function


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def get_users():
    """Get list of all users (admin only)."""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        role_filter = request.args.get("role")
        search = request.args.get("search", "").strip()
        
        query = User.query
        
        # Apply filters
        if role_filter:
            query = query.filter_by(role=role_filter)
        
        if search:
            query = query.filter(
                User.display_name.ilike(f"%{search}%") |
                User.email_or_phone.ilike(f"%{search}%")
            )
        
        # Pagination
        total = query.count()
        total_pages = math.ceil(total / per_page)
        
        users = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            "users": [user.to_dict() for user in users],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages
            }
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Users retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@admin_bp.route("/users/<user_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_user(user_id):
    """Get specific user details (admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return {"error": "User not found"}, 404
        
        return {"user": user.to_dict()}, 200
        
    except Exception as e:
        current_app.logger.error(f"User retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@admin_bp.route("/users/<user_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_user(user_id):
    """Update user details (admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return {"error": "User not found"}, 404
        
        data = request.get_json()
        
        # Update allowed fields
        if "display_name" in data:
            user.display_name = data["display_name"]
        if "role" in data:
            user.role = data["role"]
        if "is_active" in data:
            user.is_active = data["is_active"]
        if "locale" in data:
            user.locale = data["locale"]
        
        db.session.commit()
        
        return {"message": "User updated successfully", "user": user.to_dict()}, 200
        
    except Exception as e:
        current_app.logger.error(f"User update error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@admin_bp.route("/users/<user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Delete user (admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return {"error": "User not found"}, 404
        
        # Soft delete - mark as inactive
        user.is_active = False
        db.session.commit()
        
        return {"message": "User deactivated successfully"}, 200
        
    except Exception as e:
        current_app.logger.error(f"User deletion error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@admin_bp.route("/reciters", methods=["POST"])
@jwt_required()
@admin_required
def create_reciter():
    """Create new reciter (admin only)."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["name", "style", "country"]
        for field in required_fields:
            if field not in data:
                return {"error": f"Missing required field: {field}"}, 400
        
        # Check if reciter already exists
        existing = Reciter.query.filter_by(name=data["name"]).first()
        if existing:
            return {"error": "Reciter already exists"}, 409
        
        reciter = Reciter(
            name=data["name"],
            style=data["style"],
            country=data["country"],
            description=data.get("description", ""),
            is_active=data.get("is_active", True)
        )
        
        db.session.add(reciter)
        db.session.commit()
        
        return {"message": "Reciter created successfully", "reciter": reciter.to_dict()}, 201
        
    except Exception as e:
        current_app.logger.error(f"Reciter creation error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@admin_bp.route("/reciters/<int:reciter_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_reciter(reciter_id):
    """Update reciter details (admin only)."""
    try:
        reciter = Reciter.query.get(reciter_id)
        
        if not reciter:
            return {"error": "Reciter not found"}, 404
        
        data = request.get_json()
        
        # Update allowed fields
        if "name" in data:
            reciter.name = data["name"]
        if "style" in data:
            reciter.style = data["style"]
        if "country" in data:
            reciter.country = data["country"]
        if "description" in data:
            reciter.description = data["description"]
        if "is_active" in data:
            reciter.is_active = data["is_active"]
        
        db.session.commit()
        
        return {"message": "Reciter updated successfully", "reciter": reciter.to_dict()}, 200
        
    except Exception as e:
        current_app.logger.error(f"Reciter update error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@admin_bp.route("/stats/overview", methods=["GET"])
@jwt_required()
@admin_required
def get_admin_stats():
    """Get admin overview statistics."""
    try:
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        new_users_today = User.query.filter(
            User.created_at >= datetime.utcnow().date()
        ).count()
        
        # Progress statistics
        total_progress_records = Progress.query.count()
        total_playlists = Playlist.query.count()
        
        # Reciter statistics
        total_reciters = Reciter.query.count()
        active_reciters = Reciter.query.filter_by(is_active=True).count()
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "new_today": new_users_today
            },
            "content": {
                "total_progress": total_progress_records,
                "total_playlists": total_playlists
            },
            "reciters": {
                "total": total_reciters,
                "active": active_reciters
            }
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Admin stats error: {str(e)}")
        return {"error": "Internal server error"}, 500


@admin_bp.route("/system/health", methods=["GET"])
@jwt_required()
@admin_required
def system_health():
    """Check system health (admin only)."""
    try:
        
        # Database health check
        try:
            db.session.execute("SELECT 1")
            db_healthy = True
        except Exception:
            db_healthy = False
        
        # Memory usage (basic)
        memory = psutil.virtual_memory()
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected" if db_healthy else "disconnected",
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent_used": memory.percent
            }
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"System health check error: {str(e)}")
        return {"error": "Internal server error"}, 500 