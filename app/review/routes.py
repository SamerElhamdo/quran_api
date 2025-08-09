from flask import request, jsonify, current_app, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, limiter
from app.models import ReviewQueue, Progress, User, AyahIndex
from app.schemas.progress import ReviewItemSchema
from marshmallow import ValidationError
import math
from datetime import datetime, timedelta

# Create blueprint
review_bp = Blueprint("review", __name__)


@review_bp.route("/queue", methods=["GET"])
@jwt_required()
def get_review_queue():
    """Get user's review queue."""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 20, type=int), 100)
        
        query = ReviewQueue.query.filter_by(user_id=current_user_id)
        
        # Filter by status if provided
        status_filter = request.args.get("status")
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        # Order by priority and due date
        query = query.order_by(ReviewQueue.priority.desc(), ReviewQueue.due_date)
        
        # Pagination
        total = query.count()
        total_pages = math.ceil(total / per_page)
        
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            "review_items": [item.to_dict() for item in items],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages
            }
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Review queue retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@review_bp.route("/queue/<int:item_id>", methods=["GET"])
@jwt_required()
def get_review_item(item_id):
    """Get specific review item details."""
    try:
        current_user_id = get_jwt_identity()
        
        item = ReviewQueue.query.filter_by(
            id=item_id, 
            user_id=current_user_id
        ).first()
        
        if not item:
            return {"error": "Review item not found"}, 404
        
        return {"review_item": item.to_dict()}, 200
        
    except Exception as e:
        current_app.logger.error(f"Review item retrieval error: {str(e)}")
        return {"error": "Internal server error"}, 500


@review_bp.route("/queue/<int:item_id>/complete", methods=["POST"])
@jwt_required()
def complete_review(item_id):
    """Mark review item as completed."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        item = ReviewQueue.query.filter_by(
            id=item_id, 
            user_id=current_user_id
        ).first()
        
        if not item:
            return {"error": "Review item not found"}, 404
        
        # Validate completion data
        if "score" not in data:
            return {"error": "Score is required"}, 400
        
        score = data["score"]
        if not (0 <= score <= 5):
            return {"error": "Score must be between 0 and 5"}, 400
        
        # Update review item
        item.status = "completed"
        item.completed_at = datetime.utcnow()
        item.score = score
        item.notes = data.get("notes", "")
        
        # Update progress
        progress = Progress.query.filter_by(
            user_id=current_user_id,
            surah_id=item.surah_id,
            ayah_no=item.ayah_no
        ).first()
        
        if progress:
            # Update review count and last review date
            progress.review_count += 1
            progress.last_reviewed_at = datetime.utcnow()
            
            # Adjust difficulty based on score
            if score >= 4:
                # Good performance - increase interval
                progress.review_interval = min(progress.review_interval * 1.5, 30)
            elif score <= 2:
                # Poor performance - decrease interval
                progress.review_interval = max(progress.review_interval * 0.7, 1)
        
        db.session.commit()
        
        return {"message": "Review completed successfully"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Review completion error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@review_bp.route("/queue/<int:item_id>/skip", methods=["POST"])
@jwt_required()
def skip_review(item_id):
    """Skip review item (reschedule for later)."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        item = ReviewQueue.query.filter_by(
            id=item_id, 
            user_id=current_user_id
        ).first()
        
        if not item:
            return {"error": "Review item not found"}, 404
        
        # Calculate new due date (default: +1 day)
        days_to_add = data.get("days", 1)
        new_due_date = datetime.utcnow() + timedelta(days=days_to_add)
        
        # Update item
        item.due_date = new_due_date
        item.skip_count += 1
        item.last_modified = datetime.utcnow()
        
        db.session.commit()
        
        return {"message": "Review item rescheduled", "new_due_date": new_due_date.isoformat()}, 200
        
    except Exception as e:
        current_app.logger.error(f"Review skip error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@review_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_review_stats():
    """Get user's review statistics."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get review statistics
        total_reviews = ReviewQueue.query.filter_by(
            user_id=current_user_id, 
            status="completed"
        ).count()
        
        pending_reviews = ReviewQueue.query.filter_by(
            user_id=current_user_id, 
            status="pending"
        ).count()
        
        overdue_reviews = ReviewQueue.query.filter(
            ReviewQueue.user_id == current_user_id,
            ReviewQueue.status == "pending",
            ReviewQueue.due_date < datetime.utcnow()
        ).count()
        
        # Get average score
        completed_reviews = ReviewQueue.query.filter_by(
            user_id=current_user_id, 
            status="completed"
        ).all()
        
        if completed_reviews:
            avg_score = sum(item.score for item in completed_reviews) / len(completed_reviews)
        else:
            avg_score = 0
        
        # Get daily streak
        today = datetime.utcnow().date()
        streak = 0
        current_date = today
        
        while True:
            daily_reviews = ReviewQueue.query.filter(
                ReviewQueue.user_id == current_user_id,
                ReviewQueue.status == "completed",
                ReviewQueue.completed_at >= current_date,
                ReviewQueue.completed_at < current_date + timedelta(days=1)
            ).count()
            
            if daily_reviews > 0:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return {
            "total_reviews": total_reviews,
            "pending_reviews": pending_reviews,
            "overdue_reviews": overdue_reviews,
            "average_score": round(avg_score, 2),
            "daily_streak": streak,
            "last_updated": datetime.utcnow().isoformat()
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Review stats error: {str(e)}")
        return {"error": "Internal server error"}, 500


@review_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_review_queue():
    """Generate new review items for user."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get user's progress items that need review
        progress_items = Progress.query.filter_by(user_id=current_user_id).all()
        
        new_items = []
        for progress in progress_items:
            # Check if item needs review
            if progress.last_reviewed_at:
                days_since_review = (datetime.utcnow() - progress.last_reviewed_at).days
                if days_since_review >= progress.review_interval:
                    # Create review item
                    review_item = ReviewQueue(
                        user_id=current_user_id,
                        surah_id=progress.surah_id,
                        ayah_no=progress.ayah_no,
                        priority=progress.review_count + 1,  # Higher priority for items reviewed more
                        due_date=datetime.utcnow(),
                        status="pending"
                    )
                    
                    # Check if item already exists in queue
                    existing = ReviewQueue.query.filter_by(
                        user_id=current_user_id,
                        surah_id=progress.surah_id,
                        ayah_no=progress.ayah_no,
                        status="pending"
                    ).first()
                    
                    if not existing:
                        new_items.append(review_item)
        
        if new_items:
            db.session.add_all(new_items)
            db.session.commit()
            
            return {
                "message": f"Generated {len(new_items)} new review items",
                "count": len(new_items)
            }, 201
        else:
            return {"message": "No new review items needed"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Review queue generation error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500


@review_bp.route("/queue/clear-completed", methods=["DELETE"])
@jwt_required()
def clear_completed_reviews():
    """Clear completed review items from queue."""
    try:
        current_user_id = get_jwt_identity()
        
        # Delete completed items older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        deleted_count = ReviewQueue.query.filter(
            ReviewQueue.user_id == current_user_id,
            ReviewQueue.status == "completed",
            ReviewQueue.completed_at < cutoff_date
        ).delete()
        
        db.session.commit()
        
        return {"message": f"Cleared {deleted_count} completed review items"}, 200
        
    except Exception as e:
        current_app.logger.error(f"Clear completed reviews error: {str(e)}")
        db.session.rollback()
        return {"error": "Internal server error"}, 500 