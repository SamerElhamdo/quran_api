from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, limiter
from app.models import Progress, ReviewQueue, Playlist, User
from app.schemas.progress import ProgressSchema
from marshmallow import ValidationError
import math
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from . import stats_bp


@stats_bp.route("/overview", methods=["GET"])
@jwt_required()
def get_overview_stats():
    """Get user's overview statistics."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get basic counts
        total_progress = Progress.query.filter_by(user_id=current_user_id).count()
        completed_ayahs = Progress.query.filter_by(
            user_id=current_user_id, 
            status="completed"
        ).count()
        
        total_playlists = Playlist.query.filter_by(user_id=current_user_id).count()
        total_reviews = ReviewQueue.query.filter_by(
            user_id=current_user_id, 
            status="completed"
        ).count()
        
        # Calculate completion percentage
        completion_percentage = (completed_ayahs / 6236 * 100) if total_progress > 0 else 0
        
        # Get current streak
        streak = calculate_current_streak(current_user_id)
        
        # Get weekly progress
        week_start = datetime.utcnow() - timedelta(days=7)
        weekly_progress = Progress.query.filter(
            Progress.user_id == current_user_id,
            Progress.updated_at >= week_start
        ).count()
        
        return {
            "overview": {
                "total_progress": total_progress,
                "completed_ayahs": completed_ayahs,
                "completion_percentage": round(completion_percentage, 2),
                "total_playlists": total_playlists,
                "total_reviews": total_reviews,
                "current_streak": streak,
                "weekly_progress": weekly_progress
            },
            "last_updated": datetime.utcnow().isoformat()
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Overview stats error: {str(e)}")
        return {"error": "Internal server error"}, 500


@stats_bp.route("/progress", methods=["GET"])
@jwt_required()
def get_progress_stats():
    """Get detailed progress statistics."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get progress by surah
        surah_progress = db.session.query(
            Progress.surah_id,
            func.count(Progress.id).label('total_ayahs'),
            func.sum(func.case([(Progress.status == 'completed', 1)], else_=0)).label('completed_ayahs')
        ).filter_by(user_id=current_user_id).group_by(Progress.surah_id).all()
        
        # Get progress by status
        status_counts = db.session.query(
            Progress.status,
            func.count(Progress.id).label('count')
        ).filter_by(user_id=current_user_id).group_by(Progress.status).all()
        
        # Get recent activity
        recent_activity = Progress.query.filter_by(
            user_id=current_user_id
        ).order_by(Progress.updated_at.desc()).limit(10).all()
        
        return {
            "surah_progress": [
                {
                    "surah_id": item.surah_id,
                    "total_ayahs": item.total_ayahs,
                    "completed_ayahs": item.completed_ayahs,
                    "completion_percentage": round((item.completed_ayahs / item.total_ayahs * 100), 2)
                }
                for item in surah_progress
            ],
            "status_distribution": [
                {
                    "status": item.status,
                    "count": item.count
                }
                for item in status_counts
            ],
            "recent_activity": [
                {
                    "surah_id": item.surah_id,
                    "ayah_no": item.ayah_no,
                    "status": item.status,
                    "updated_at": item.updated_at.isoformat()
                }
                for item in recent_activity
            ]
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Progress stats error: {str(e)}")
        return {"error": "Internal server error"}, 500


@stats_bp.route("/timeline", methods=["GET"])
@jwt_required()
def get_timeline_stats():
    """Get progress timeline statistics."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get daily progress for the last 30 days
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)
        
        daily_progress = db.session.query(
            func.date(Progress.updated_at).label('date'),
            func.count(Progress.id).label('progress_count'),
            func.sum(func.case([(Progress.status == 'completed', 1)], else_=0)).label('completed_count')
        ).filter(
            and_(
                Progress.user_id == current_user_id,
                func.date(Progress.updated_at) >= start_date,
                func.date(Progress.updated_at) <= end_date
            )
        ).group_by(func.date(Progress.updated_at)).all()
        
        # Get weekly progress for the last 12 weeks
        weekly_progress = db.session.query(
            func.strftime('%Y-%W', Progress.updated_at).label('week'),
            func.count(Progress.id).label('progress_count'),
            func.sum(func.case([(Progress.status == 'completed', 1)], else_=0)).label('completed_count')
        ).filter(
            and_(
                Progress.user_id == current_user_id,
                Progress.updated_at >= datetime.utcnow() - timedelta(weeks=12)
            )
        ).group_by(func.strftime('%Y-%W', Progress.updated_at)).all()
        
        return {
            "daily_progress": [
                {
                    "date": item.date.isoformat(),
                    "progress_count": item.progress_count,
                    "completed_count": item.completed_count
                }
                for item in daily_progress
            ],
            "weekly_progress": [
                {
                    "week": item.week,
                    "progress_count": item.progress_count,
                    "completed_count": item.completed_count
                }
                for item in weekly_progress
            ]
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Timeline stats error: {str(e)}")
        return {"error": "Internal server error"}, 500


@stats_bp.route("/achievements", methods=["GET"])
@jwt_required()
def get_achievements():
    """Get user's achievements and milestones."""
    try:
        current_user_id = get_jwt_identity()
        
        # Get user's progress
        total_completed = Progress.query.filter_by(
            user_id=current_user_id, 
            status="completed"
        ).count()
        
        # Define achievements
        achievements = []
        
        # First ayah achievement
        if total_completed >= 1:
            achievements.append({
                "id": "first_ayah",
                "title": "First Steps",
                "description": "Completed your first ayah",
                "unlocked_at": "achieved",
                "icon": "🌟"
            })
        
        # 10 ayahs achievement
        if total_completed >= 10:
            achievements.append({
                "id": "ten_ayahs",
                "title": "Getting Started",
                "description": "Completed 10 ayahs",
                "unlocked_at": "achieved",
                "icon": "📚"
            })
        
        # 100 ayahs achievement
        if total_completed >= 100:
            achievements.append({
                "id": "hundred_ayahs",
                "title": "Century Club",
                "description": "Completed 100 ayahs",
                "unlocked_at": "achieved",
                "icon": "🏆"
            })
        
        # First surah completion
        first_surah = db.session.query(
            Progress.surah_id,
            func.count(Progress.id).label('total_ayahs'),
            func.sum(func.case([(Progress.status == 'completed', 1)], else_=0)).label('completed_ayahs')
        ).filter_by(user_id=current_user_id).group_by(Progress.surah_id).having(
            func.sum(func.case([(Progress.status == 'completed', 1)], else_=0)) == 
            func.count(Progress.id)
        ).first()
        
        if first_surah:
            achievements.append({
                "id": "first_surah",
                "title": "Surah Master",
                "description": f"Completed Surah {first_surah.surah_id}",
                "unlocked_at": "achieved",
                "icon": "📖"
            })
        
        # Streak achievements
        current_streak = calculate_current_streak(current_user_id)
        
        if current_streak >= 7:
            achievements.append({
                "id": "week_streak",
                "title": "Week Warrior",
                "description": "Maintained a 7-day streak",
                "unlocked_at": "achieved",
                "icon": "🔥"
            })
        
        if current_streak >= 30:
            achievements.append({
                "id": "month_streak",
                "title": "Monthly Master",
                "description": "Maintained a 30-day streak",
                "unlocked_at": "achieved",
                "icon": "💎"
            })
        
        # Review achievements
        total_reviews = ReviewQueue.query.filter_by(
            user_id=current_user_id, 
            status="completed"
        ).count()
        
        if total_reviews >= 50:
            achievements.append({
                "id": "reviewer",
                "title": "Dedicated Reviewer",
                "description": "Completed 50 reviews",
                "unlocked_at": "achieved",
                "icon": "🔄"
            })
        
        return {
            "achievements": achievements,
            "total_achievements": len(achievements),
            "total_possible": 8  # Total number of achievements available
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Achievements error: {str(e)}")
        return {"error": "Internal server error"}, 500


@stats_bp.route("/leaderboard", methods=["GET"])
@jwt_required()
def get_leaderboard():
    """Get leaderboard of top users."""
    try:
        # Get top users by completion percentage
        top_users = db.session.query(
            User.id,
            User.display_name,
            func.count(Progress.id).label('total_progress'),
            func.sum(func.case([(Progress.status == 'completed', 1)], else_=0)).label('completed_ayahs')
        ).join(Progress, User.id == Progress.user_id).group_by(User.id, User.display_name).order_by(
            func.sum(func.case([(Progress.status == 'completed', 1)], else_=0)).desc()
        ).limit(20).all()
        
        # Get current user's rank
        current_user_id = get_jwt_identity()
        current_user_progress = db.session.query(
            func.count(Progress.id).label('total_progress'),
            func.sum(func.case([(Progress.status == 'completed', 1)], else_=0)).label('completed_ayahs')
        ).filter_by(user_id=current_user_id).first()
        
        if current_user_progress and current_user_progress.completed_ayahs > 0:
            # Calculate rank
            users_ahead = db.session.query(func.count(User.id)).join(
                Progress, User.id == Progress.user_id
            ).group_by(User.id).having(
                func.sum(func.case([(Progress.status == 'completed', 1)], else_=0)) > 
                current_user_progress.completed_ayahs
            ).count()
            
            current_user_rank = users_ahead + 1
        else:
            current_user_rank = None
        
        return {
            "leaderboard": [
                {
                    "rank": idx + 1,
                    "user_id": user.id,
                    "display_name": user.display_name,
                    "completed_ayahs": user.completed_ayahs,
                    "total_progress": user.total_progress,
                    "completion_percentage": round((user.completed_ayahs / user.total_progress * 100), 2)
                }
                for idx, user in enumerate(top_users)
            ],
            "current_user": {
                "rank": current_user_rank,
                "completed_ayahs": current_user_progress.completed_ayahs if current_user_progress else 0,
                "total_progress": current_user_progress.total_progress if current_user_progress else 0
            } if current_user_progress else None
        }, 200
        
    except Exception as e:
        current_app.logger.error(f"Leaderboard error: {str(e)}")
        return {"error": "Internal server error"}, 500


def calculate_current_streak(user_id):
    """Calculate user's current daily streak."""
    try:
        today = datetime.utcnow().date()
        streak = 0
        current_date = today
        
        while True:
            # Check if user had any activity on this date
            daily_activity = db.session.query(
                func.count(Progress.id)
            ).filter(
                and_(
                    Progress.user_id == user_id,
                    func.date(Progress.updated_at) == current_date
                )
            ).scalar()
            
            if daily_activity > 0:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
        
    except Exception:
        return 0 