from flask import request, jsonify, current_app, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, limiter
from app.models import Reciter, AyahIndex, User, UserSettings
from app.schemas.common import PaginationSchema
from marshmallow import ValidationError
import math

# Create blueprint
content_bp = Blueprint("content", __name__)


@content_bp.route("/reciters", methods=["GET"])
def get_reciters():
    """Get list of available reciters."""
    try:
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        
        query = Reciter.query
        
        # Pagination
        total = query.count()
        total_pages = math.ceil(total / per_page)
        
        reciters = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            "reciters": [reciter.to_dict() for reciter in reciters],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages
            }
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Reciters retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@content_bp.route("/reciters/<int:reciter_id>", methods=["GET"])
def get_reciter(reciter_id):
    """Get specific reciter details."""
    try:
        reciter = Reciter.query.get(reciter_id)
        
        if not reciter:
            return {"error": "Reciter not found"}, 404
        
        return {"reciter": reciter.to_dict()}, 200
        
    except Exception as e:
        current_app.logger.error(f"Reciter retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@content_bp.route("/search", methods=["GET"])
def search_quran():
    """Search Quran text."""
    try:
        query = request.args.get("q", "").strip()
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        
        if not query or len(query) < 2:
            return {"error": "Search query must be at least 2 characters long"}, 400
        
        # Search in ayah index
        search_results = AyahIndex.query.filter(
            AyahIndex.text_plain.ilike(f"%{query}%")
        ).order_by(AyahIndex.surah_id, AyahIndex.ayah_no)
        
        # Pagination
        total = search_results.count()
        total_pages = math.ceil(total / per_page)
        
        results = search_results.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            "results": [result.to_dict() for result in results],
            "query": query,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages
            }
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Search error: {str(e)}")
        return {"error": "Internal server error"}, 500


@content_bp.route("/surah/<int:surah_id>", methods=["GET"])
def get_surah_info(surah_id):
    """Get surah information and structure."""
    try:
        if surah_id < 1 or surah_id > 114:
            return {"error": "Invalid surah ID. Must be between 1 and 114"}, 400
        
        # Get surah details (this would need to be implemented based on your data structure)
        # For now, return basic structure
        surah_info = {
            "id": surah_id,
            "name_arabic": f"Surah {surah_id}",  # This should come from your data
            "name_english": f"Surah {surah_id}",  # This should come from your data
            "total_ayahs": 0,  # This should come from your data
            "revelation_type": "Meccan" if surah_id <= 87 else "Medinan",  # Basic logic
            "juz": 0  # This should come from your data
        }
        
        return {"surah": surah_info}, 200
        
    except Exception as e:
        current_app.logger.error(f"Surah info retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@content_bp.route("/surah/<int:surah_id>/ayah/<int:ayah_no>", methods=["GET"])
def get_ayah_info(surah_id, ayah_no):
    """Get specific ayah information."""
    try:
        if surah_id < 1 or surah_id > 114:
            return {"error": "Invalid surah ID. Must be between 1 and 114"}, 400
        
        if ayah_no < 1:
            return {"error": "Invalid ayah number. Must be greater than 0"}, 400
        
        # Get ayah details (this would need to be implemented based on your data structure)
        ayah_info = {
            "surah_id": surah_id,
            "ayah_no": ayah_no,
            "text_arabic": f"Ayah {ayah_no} from Surah {surah_id}",  # This should come from your data
            "text_translation": f"Translation of ayah {ayah_no} from surah {surah_id}",  # This should come from your data
            "page": 0,  # This should come from your data
            "juz": 0,  # This should come from your data
            "hizb": 0  # This should come from your data
        }
        
        return {"ayah": ayah_info}, 200
        
    except Exception as e:
        current_app.logger.error(f"Ayah info retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@content_bp.route("/audio-url", methods=["GET"])
@jwt_required()
def get_audio_url():
    """Get audio URL for specific ayah with user preferences."""
    try:
        current_user_id = get_jwt_identity()
        
        surah_id = request.args.get("surah_id", type=int)
        ayah_no = request.args.get("ayah_no", type=int)
        reciter_id = request.args.get("reciter_id", type=int)
        
        if not surah_id or not ayah_no:
            return {"error": "Surah ID and ayah number are required"}, 400
        
        if surah_id < 1 or surah_id > 114:
            return {"error": "Invalid surah ID. Must be between 1 and 114"}, 400
        
        if ayah_no < 1:
            return {"error": "Invalid ayah number. Must be greater than 0"}, 400
        
        # Get user's preferred reciter if not specified
        if not reciter_id:
            user_settings = UserSettings.query.filter_by(user_id=current_user_id).first()
            if user_settings and user_settings.reciter_id:
                reciter_id = user_settings.reciter_id
            else:
                # Default reciter
                reciter_id = 1
        
        # Get reciter
        reciter = Reciter.query.get(reciter_id)
        if not reciter:
            return {"error": "Reciter not found"}, 404
        
        # Construct audio URL
        # This is a placeholder - you'll need to implement the actual URL construction
        # based on your audio file structure
        audio_url = f"{reciter.base_url}/surah_{surah_id:03d}/ayah_{ayah_no:03d}.mp3"
        
        return {
            "audio_url": audio_url,
            "reciter": reciter.to_dict(),
            "surah_id": surah_id,
            "ayah_no": ayah_no
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Audio URL generation error: {str(e)}")
        return {"error": "Internal server error"}, 500


@content_bp.route("/user-settings", methods=["GET"])
@jwt_required()
def get_user_settings():
    """Get current user's content preferences."""
    try:
        current_user_id = get_jwt_identity()
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        
        if not settings:
            return {"error": "User settings not found"}, 404
        
        return {"settings": settings.to_dict()}, 200
        
    except Exception as e:
        current_app.logger.error(f"User settings retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@content_bp.route("/user-settings", methods=["PUT"])
@jwt_required()
def update_user_settings():
    """Update current user's content preferences."""
    try:
        current_user_id = get_jwt_identity()
        settings = UserSettings.query.filter_by(user_id=current_user_id).first()
        
        if not settings:
            return {"error": "User settings not found"}, 404
        
        data = request.get_json()
        
        # Update allowed fields
        if "reciter_id" in data:
            # Verify reciter exists
            reciter = Reciter.query.get(data["reciter_id"])
            if not reciter:
                return {"error": "Invalid reciter ID"}, 400
            settings.reciter_id = data["reciter_id"]
        
        if "default_speed" in data:
            speed = float(data["default_speed"])
            if not (0.5 <= speed <= 3.0):
                return {"error": "Speed must be between 0.5 and 3.0"}, 400
            settings.default_speed = speed
        
        if "tajweed_enabled" in data:
            settings.tajweed_enabled = bool(data["tajweed_enabled"])
        
        if "font_scale" in data:
            scale = float(data["font_scale"])
            if not (0.8 <= scale <= 2.0):
                return {"error": "Font scale must be between 0.8 and 2.0"}, 400
            settings.font_scale = scale
        
        db.session.commit()
        
        return {
            "message": "Settings updated successfully",
            "settings": settings.to_dict()
        }, 200
        
    except ValueError:
        return {"error": "Invalid data format"}, 400
    except Exception as e:
        current_app.logger.error(f"Settings update error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500 