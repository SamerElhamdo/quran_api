from flask import request, jsonify, current_app, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, limiter
from app.models import Playlist, PlaylistItem, User
from marshmallow import ValidationError
import math

# Create blueprint
playlists_bp = Blueprint("playlists", __name__)


@playlists_bp.route("/", methods=["GET"])
@jwt_required()
def get_playlists():
    """Get user's playlists."""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        
        query = Playlist.query.filter_by(user_id=current_user_id)
        
        # Pagination
        total = query.count()
        total_pages = math.ceil(total / per_page)
        
        playlists = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            "playlists": [playlist.to_dict() for playlist in playlists],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages
            }
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Playlists retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@playlists_bp.route("/", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def create_playlist():
    """Create a new playlist."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get("title"):
            return {"error": "Playlist title is required"}, 400
        
        # Create playlist
        playlist = Playlist(
            user_id=current_user_id,
            title=data["title"]
        )
        
        db.session.add(playlist)
        db.session.commit()
        
        return {
            "message": "Playlist created successfully",
            "playlist": playlist.to_dict()
        }, 201
        
    except Exception as e:
        current_app.logger.error(f"Playlist creation error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@playlists_bp.route("/<uuid:playlist_id>", methods=["GET"])
@jwt_required()
def get_playlist(playlist_id):
    """Get specific playlist details."""
    try:
        current_user_id = get_jwt_identity()
        playlist = Playlist.query.filter_by(
            id=playlist_id,
            user_id=current_user_id
        ).first()
        
        if not playlist:
            return {"error": "Playlist not found"}, 404
        
        return {"playlist": playlist.to_dict()}, 200
        
    except Exception as e:
        current_app.logger.error(f"Playlist retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@playlists_bp.route("/<uuid:playlist_id>", methods=["PUT"])
@jwt_required()
def update_playlist(playlist_id):
    """Update playlist details."""
    try:
        current_user_id = get_jwt_identity()
        playlist = Playlist.query.filter_by(
            id=playlist_id,
            user_id=current_user_id
        ).first()
        
        if not playlist:
            return {"error": "Playlist not found"}, 404
        
        data = request.get_json()
        
        if "title" in data:
            playlist.title = data["title"]
        
        db.session.commit()
        
        return {
            "message": "Playlist updated successfully",
            "playlist": playlist.to_dict()
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Playlist update error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@playlists_bp.route("/<uuid:playlist_id>", methods=["DELETE"])
@jwt_required()
def delete_playlist(playlist_id):
    """Delete a playlist."""
    try:
        current_user_id = get_jwt_identity()
        playlist = Playlist.query.filter_by(
            id=playlist_id,
            user_id=current_user_id
        ).first()
        
        if not playlist:
            return {"error": "Playlist not found"}, 404
        
        db.session.delete(playlist)
        db.session.commit()
        
        return {"message": "Playlist deleted successfully"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Playlist deletion error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@playlists_bp.route("/<uuid:playlist_id>/items", methods=["POST"])
@jwt_required()
@limiter.limit("20 per minute")
def add_playlist_item(playlist_id):
    """Add item to playlist."""
    try:
        current_user_id = get_jwt_identity()
        playlist = Playlist.query.filter_by(
            id=playlist_id,
            user_id=current_user_id
        ).first()
        
        if not playlist:
            return {"error": "Playlist not found"}, 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["from_surah", "from_ayah", "to_surah", "to_ayah"]
        for field in required_fields:
            if field not in data:
                return {"error": f"Field '{field}' is required"}, 400
        
        # Validate surah and ayah numbers
        if not (1 <= data["from_surah"] <= 114 and 1 <= data["to_surah"] <= 114):
            return {"error": "Invalid surah ID. Must be between 1 and 114"}, 400
        
        if data["from_ayah"] < 1 or data["to_ayah"] < 1:
            return {"error": "Invalid ayah number. Must be greater than 0"}, 400
        
        # Get next position
        max_position = db.session.query(db.func.max(PlaylistItem.position)).filter_by(
            playlist_id=playlist_id
        ).scalar() or 0
        
        # Create playlist item
        item = PlaylistItem(
            playlist_id=playlist_id,
            position=max_position + 1,
            from_surah=data["from_surah"],
            from_ayah=data["from_ayah"],
            to_surah=data["to_surah"],
            to_ayah=data["to_ayah"],
            repeat=data.get("repeat", 3),
            speed=data.get("speed", 1.0)
        )
        
        db.session.add(item)
        db.session.commit()
        
        return {
            "message": "Item added to playlist successfully",
            "item": item.to_dict()
        }, 201
        
    except ValueError:
        return {"error": "Invalid data format"}, 400
    except Exception as e:
        current_app.logger.error(f"Playlist item addition error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@playlists_bp.route("/<uuid:playlist_id>/items/<int:position>", methods=["PUT"])
@jwt_required()
def update_playlist_item(playlist_id, position):
    """Update playlist item."""
    try:
        current_user_id = get_jwt_identity()
        playlist = Playlist.query.filter_by(
            id=playlist_id,
            user_id=current_user_id
        ).first()
        
        if not playlist:
            return {"error": "Playlist not found"}, 404
        
        item = PlaylistItem.query.filter_by(
            playlist_id=playlist_id,
            position=position
        ).first()
        
        if not item:
            return {"error": "Playlist item not found"}, 404
        
        data = request.get_json()
        
        # Update allowed fields
        if "repeat" in data:
            repeat = int(data["repeat"])
            if not (1 <= repeat <= 10):
                return {"error": "Repeat count must be between 1 and 10"}, 400
            item.repeat = repeat
        
        if "speed" in data:
            speed = float(data["speed"])
            if not (0.5 <= speed <= 3.0):
                return {"error": "Speed must be between 0.5 and 3.0"}, 400
            item.speed = speed
        
        db.session.commit()
        
        return {
            "message": "Playlist item updated successfully",
            "item": item.to_dict()
        }, 200
        
    except ValueError:
        return {"error": "Invalid data format"}, 400
    except Exception as e:
        current_app.logger.error(f"Playlist item update error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@playlists_bp.route("/<uuid:playlist_id>/items/<int:position>", methods=["DELETE"])
@jwt_required()
def delete_playlist_item(playlist_id, position):
    """Delete playlist item."""
    try:
        current_user_id = get_jwt_identity()
        playlist = Playlist.query.filter_by(
            id=playlist_id,
            user_id=current_user_id
        ).first()
        
        if not playlist:
            return {"error": "Playlist not found"}, 404
        
        item = PlaylistItem.query.filter_by(
            playlist_id=playlist_id,
            position=position
        ).first()
        
        if not item:
            return {"error": "Playlist item not found"}, 404
        
        db.session.delete(item)
        
        # Reorder remaining items
        remaining_items = PlaylistItem.query.filter_by(
            playlist_id=playlist_id
        ).filter(PlaylistItem.position > position).order_by(PlaylistItem.position).all()
        
        for i, remaining_item in enumerate(remaining_items):
            remaining_item.position = position + i
        
        db.session.commit()
        
        return {"message": "Playlist item deleted successfully"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Playlist item deletion error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@playlists_bp.route("/<uuid:playlist_id>/items/reorder", methods=["POST"])
@jwt_required()
def reorder_playlist_items(playlist_id):
    """Reorder playlist items."""
    try:
        current_user_id = get_jwt_identity()
        playlist = Playlist.query.filter_by(
            id=playlist_id,
            user_id=current_user_id
        ).first()
        
        if not playlist:
            return {"error": "Playlist not found"}, 404
        
        data = request.get_json()
        
        if "positions" not in data or not isinstance(data["positions"], list):
            return {"error": "Positions array is required"}, 400
        
        # Validate positions
        current_positions = {item.position for item in playlist.items}
        new_positions = set(data["positions"])
        
        if current_positions != new_positions:
            return {"error": "Invalid positions array"}, 400
        
        # Reorder items
        for new_position, old_position in enumerate(data["positions"], 1):
            item = PlaylistItem.query.filter_by(
                playlist_id=playlist_id,
                position=old_position
            ).first()
            if item:
                item.position = new_position
        
        db.session.commit()
        
        return {"message": "Playlist items reordered successfully"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Playlist reorder error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500 