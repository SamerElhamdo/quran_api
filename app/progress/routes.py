from flask import request, jsonify, current_app, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, limiter
from app.models import Progress, User, AyahIndex
from app.schemas.progress import ProgressSchema, ProgressUpdateSchema
from marshmallow import ValidationError
import math
from datetime import datetime

# Create blueprint
progress_bp = Blueprint("progress", __name__)


@progress_bp.route("/", methods=["GET"])
@jwt_required()
def get_user_progress():
    """Get current user's progress."""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        status_filter = request.args.get("status")
        surah_filter = request.args.get("surah_id", type=int)
        
        query = Progress.query.filter_by(user_id=current_user_id)
        
        # Apply filters
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        if surah_filter:
            query = query.filter_by(surah_id=surah_filter)
        
        # Order by surah_id, then ayah_no
        query = query.order_by(Progress.surah_id, Progress.ayah_no)
        
        # Pagination
        total = query.count()
        total_pages = math.ceil(total / per_page)
        
        progress_items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        progress_schema = ProgressSchema(many=True)
        progress_data = progress_schema.dump(progress_items)
        
        return {
            "progress": progress_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages
            }
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Progress retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@progress_bp.route("/", methods=["POST"])
@jwt_required()
@limiter.limit("30 per minute")
def create_progress():
    """Create or update progress for an ayah."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input data
        schema = ProgressUpdateSchema()
        validated_data = schema.load(data)
        
        # Check if progress already exists
        existing_progress = Progress.query.filter_by(
            user_id=current_user_id,
            surah_id=validated_data["surah_id"],
            ayah_no=validated_data["ayah_no"]
        ).first()
        
        if existing_progress:
            # Update existing progress
            existing_progress.status = validated_data["status"]
            existing_progress.attempts += 1
            existing_progress.last_attempted_at = datetime.utcnow()
            existing_progress.updated_at = datetime.utcnow()
            
            if validated_data["status"] == "completed":
                existing_progress.completed_at = datetime.utcnow()
                existing_progress.review_interval = 1  # Start with 1 day interval
            
            db.session.commit()
            
            progress_schema = ProgressSchema()
            return {
                "message": "Progress updated successfully",
                "progress": progress_schema.dump(existing_progress)
            }, 200
        else:
            # Create new progress
            new_progress = Progress(
                user_id=current_user_id,
                surah_id=validated_data["surah_id"],
                ayah_no=validated_data["ayah_no"],
                status=validated_data["status"],
                attempts=1,
                last_attempted_at=datetime.utcnow(),
                review_interval=1 if validated_data["status"] == "completed" else 0
            )
            
            if validated_data["status"] == "completed":
                new_progress.completed_at = datetime.utcnow()
            
            db.session.add(new_progress)
            db.session.commit()
            
            progress_schema = ProgressSchema()
            return {
                "message": "Progress created successfully",
                "progress": progress_schema.dump(new_progress)
            }, 201
        
    except ValidationError as e:
        return {"error": "Validation error", "details": e.messages}, 400
    except Exception as e:
        current_app.logger.error(f"Progress creation error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@progress_bp.route("/<int:surah_id>/<int:ayah_no>", methods=["GET"])
@jwt_required()
def get_ayah_progress(surah_id, ayah_no):
    """Get progress for a specific ayah."""
    try:
        current_user_id = get_jwt_identity()
        
        if surah_id < 1 or surah_id > 114:
            return {"error": "Invalid surah ID. Must be between 1 and 114"}, 400
        
        if ayah_no < 1:
            return {"error": "Invalid ayah number. Must be greater than 0"}, 400
        
        progress = Progress.query.filter_by(
            user_id=current_user_id,
            surah_id=surah_id,
            ayah_no=ayah_no
        ).first()
        
        if not progress:
            return {"progress": None}, 200
        
        progress_schema = ProgressSchema()
        return {"progress": progress_schema.dump(progress)}, 200
        
    except Exception as e:
        current_app.logger.error(f"Ayah progress retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@progress_bp.route("/<int:surah_id>/<int:ayah_no>", methods=["PUT"])
@jwt_required()
def update_ayah_progress(surah_id, ayah_no):
    """Update progress for a specific ayah."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if surah_id < 1 or surah_id > 114:
            return {"error": "Invalid surah ID. Must be between 1 and 114"}, 400
        
        if ayah_no < 1:
            return {"error": "Invalid ayah number. Must be greater than 0"}, 400
        
        progress = Progress.query.filter_by(
            user_id=current_user_id,
            surah_id=surah_id,
            ayah_no=ayah_no
        ).first()
        
        if not progress:
            return {"error": "Progress not found. Create progress first."}, 404
        
        # Update progress
        if "status" in data:
            progress.status = data["status"]
            if data["status"] == "completed" and not progress.completed_at:
                progress.completed_at = datetime.utcnow()
                progress.review_interval = 1
        
        if "notes" in data:
            progress.notes = data["notes"]
        
        progress.attempts += 1
        progress.last_attempted_at = datetime.utcnow()
        progress.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        progress_schema = ProgressSchema()
        return {
            "message": "Progress updated successfully",
            "progress": progress_schema.dump(progress)
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Progress update error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@progress_bp.route("/<int:surah_id>/<int:ayah_no>", methods=["DELETE"])
@jwt_required()
def delete_ayah_progress(surah_id, ayah_no):
    """Delete progress for a specific ayah."""
    try:
        current_user_id = get_jwt_identity()
        
        if surah_id < 1 or surah_id > 114:
            return {"error": "Invalid surah ID. Must be between 1 and 114"}, 400
        
        if ayah_no < 1:
            return {"error": "Invalid ayah number. Must be greater than 0"}, 400
        
        progress = Progress.query.filter_by(
            user_id=current_user_id,
            surah_id=surah_id,
            ayah_no=ayah_no
        ).first()
        
        if not progress:
            return {"error": "Progress not found"}, 404
        
        db.session.delete(progress)
        db.session.commit()
        
        return {"message": "Progress deleted successfully"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Progress deletion error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@progress_bp.route("/surah/<int:surah_id>", methods=["GET"])
@jwt_required()
def get_surah_progress(surah_id):
    """Get progress summary for a specific surah."""
    try:
        current_user_id = get_jwt_identity()
        
        if surah_id < 1 or surah_id > 114:
            return {"error": "Invalid surah ID. Must be between 1 and 114"}, 400
        
        # Get all progress items for this surah
        progress_items = Progress.query.filter_by(
            user_id=current_user_id,
            surah_id=surah_id
        ).all()
        
        if not progress_items:
            return {
                "surah_id": surah_id,
                "total_ayahs": 0,
                "completed_ayahs": 0,
                "in_progress_ayahs": 0,
                "not_started_ayahs": 0,
                "completion_percentage": 0
            }, 200
        
        # Calculate statistics
        total_ayahs = len(progress_items)
        completed_ayahs = len([p for p in progress_items if p.status == "completed"])
        in_progress_ayahs = len([p for p in progress_items if p.status == "in_progress"])
        not_started_ayahs = len([p for p in progress_items if p.status == "not_started"])
        
        completion_percentage = (completed_ayahs / total_ayahs * 100) if total_ayahs > 0 else 0
        
        return {
            "surah_id": surah_id,
            "total_ayahs": total_ayahs,
            "completed_ayahs": completed_ayahs,
            "in_progress_ayahs": in_progress_ayahs,
            "not_started_ayahs": not_started_ayahs,
            "completion_percentage": round(completion_percentage, 2)
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Surah progress error: {str(e)}")
        return {"error": "Internal server error"}, 500


@progress_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_progress_summary():
    """Get overall progress summary for the user."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get overall statistics
        total_progress = Progress.query.filter_by(user_id=current_user_id).count()
        completed_ayahs = Progress.query.filter_by(
            user_id=current_user_id, 
            status="completed"
        ).count()
        in_progress_ayahs = Progress.query.filter_by(
            user_id=current_user_id, 
            status="in_progress"
        ).count()
        not_started_ayahs = Progress.query.filter_by(
            user_id=current_user_id, 
            status="not_started"
        ).count()
        
        # Calculate completion percentage (total Quran has 6236 ayahs)
        total_quran_ayahs = 6236
        overall_completion = (completed_ayahs / total_quran_ayahs * 100) if total_quran_ayahs > 0 else 0
        
        # Get recent activity
        recent_progress = Progress.query.filter_by(
            user_id=current_user_id
        ).order_by(Progress.updated_at.desc()).limit(5).all()
        
        progress_schema = ProgressSchema(many=True)
        recent_data = progress_schema.dump(recent_progress)
        
        return {
            "summary": {
                "total_progress_items": total_progress,
                "completed_ayahs": completed_ayahs,
                "in_progress_ayahs": in_progress_ayahs,
                "not_started_ayahs": not_started_ayahs,
                "overall_completion_percentage": round(overall_completion, 2),
                "total_quran_ayahs": total_quran_ayahs
            },
            "recent_activity": recent_data
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Progress summary error: {str(e)}")
        return {"error": "Internal server error"}, 500 