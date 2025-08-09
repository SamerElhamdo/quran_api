from flask import request, jsonify, current_app, Blueprint
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, limiter
from app.models import User, UserSettings
from app.schemas.auth import LoginSchema, RegisterSchema, UserSchema
from marshmallow import ValidationError
import uuid

# Create blueprint
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    """User registration endpoint."""
    try:
        data = request.get_json()
        schema = RegisterSchema()
        validated_data = schema.load(data)
        
        # Check if user already exists
        existing_user = User.query.filter_by(
            email_or_phone=validated_data["email_or_phone"]
        ).first()
        
        if existing_user:
            return {"error": "User already exists"}, 409
        
        # Create new user
        user = User(
            email_or_phone=validated_data["email_or_phone"],
            password_hash=generate_password_hash(validated_data["password"]),
            display_name=validated_data["display_name"],
            locale=validated_data.get("locale", "ar")
        )
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create default user settings
        settings = UserSettings(
            user_id=user.id,
            default_speed=1.0,
            tajweed_enabled=True,
            font_scale=1.0
        )
        
        db.session.add(settings)
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        user_schema = UserSchema()
        user_data = user_schema.dump(user)
        
        return {
            "message": "User registered successfully",
            "user": user_data,
            "access_token": access_token,
            "refresh_token": refresh_token
        }, 201
        
    except ValidationError as e:
        return {"error": "Validation error", "details": e.messages}, 400
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        schema = LoginSchema()
        validated_data = schema.load(data)
        
        # Find user
        user = User.query.filter_by(
            email_or_phone=validated_data["email_or_phone"]
        ).first()
        
        if not user or not check_password_hash(user.password_hash, validated_data["password"]):
            return {"error": "Invalid credentials"}, 401
        
        # Generate tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        user_schema = UserSchema()
        user_data = user_schema.dump(user)
        
        return {
            "message": "Login successful",
            "user": user_data,
            "access_token": access_token,
            "refresh_token": refresh_token
        }, 200
        
    except ValidationError as e:
        return {"error": "Validation error", "details": e.messages}, 400
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return {"error": "Internal server error"}, 500


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        
        return {
            "access_token": new_access_token
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return {"error": "Internal server error"}, 500


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get current user profile."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return {"error": "User not found"}, 404
        
        user_schema = UserSchema()
        user_data = user_schema.dump(user)
        
        return {"user": user_data}, 200
        
    except Exception as e:
        current_app.logger.error(f"Profile retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update current user profile."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return {"error": "User not found"}, 404
        
        data = request.get_json()
        
        # Update allowed fields
        if "display_name" in data:
            user.display_name = data["display_name"]
        
        if "locale" in data:
            user.locale = data["locale"]
        
        db.session.commit()
        
        user_schema = UserSchema()
        user_data = user_schema.dump(user)
        
        return {
            "message": "Profile updated successfully",
            "user": user_data
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Profile update error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
@limiter.limit("5 per minute")
def change_password():
    """Change user password."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return {"error": "User not found"}, 404
        
        data = request.get_json()
        
        if not data.get("current_password") or not data.get("new_password"):
            return {"error": "Current and new password are required"}, 400
        
        # Verify current password
        if not check_password_hash(user.password_hash, data["current_password"]):
            return {"error": "Current password is incorrect"}, 401
        
        # Update password
        user.password_hash = generate_password_hash(data["new_password"])
        db.session.commit()
        
        return {"message": "Password changed successfully"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Password change error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500 