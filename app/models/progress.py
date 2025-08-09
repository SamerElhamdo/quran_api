import uuid
from datetime import date, datetime
from sqlalchemy import Column, Integer, Date, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.extensions import db


class Progress(db.Model):
    """User progress tracking using SM-2 algorithm."""
    
    __tablename__ = "progress"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    surah_id = Column(Integer, primary_key=True)
    ayah_no = Column(Integer, primary_key=True)
    ef = Column(Numeric(3, 2), nullable=False, default=2.5)  # Easiness factor
    interval_days = Column(Integer, nullable=False, default=0)  # Days until next review
    due = Column(Date, nullable=False, default=func.current_date())
    lapses = Column(Integer, nullable=False, default=0)  # Number of failures
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress")
    
    __table_args__ = (
        UniqueConstraint("user_id", "surah_id", "ayah_no", name="uq_progress_user_surah_ayah"),
    )
    
    def __repr__(self):
        return f"<Progress(user_id={self.user_id}, surah_id={self.surah_id}, ayah_no={self.ayah_no})>"
    
    def to_dict(self) -> dict:
        """Convert progress to dictionary for API responses."""
        return {
            "user_id": str(self.user_id),
            "surah_id": self.surah_id,
            "ayah_no": self.ayah_no,
            "ef": float(self.ef) if self.ef else 2.5,
            "interval_days": self.interval_days,
            "due": self.due.isoformat() if self.due else None,
            "lapses": self.lapses,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def is_due(self) -> bool:
        """Check if this verse is due for review."""
        return self.due <= date.today()
    
    def get_next_due_date(self) -> date:
        """Calculate the next due date based on current interval."""
        from datetime import timedelta
        return date.today() + timedelta(days=self.interval_days)


class ReviewQueue(db.Model):
    """Daily review queue for users."""
    
    __tablename__ = "review_queue"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    surah_id = Column(Integer, nullable=False)
    ayah_no = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="review_queue")
    
    __table_args__ = (
        UniqueConstraint("user_id", "due_date", "surah_id", "ayah_no", name="uq_review_queue_user_date_surah_ayah"),
    )
    
    def __repr__(self):
        return f"<ReviewQueue(user_id={self.user_id}, due_date={self.due_date}, surah_id={self.surah_id}, ayah_no={self.ayah_no})>"
    
    def to_dict(self) -> dict:
        """Convert review queue item to dictionary for API responses."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "surah_id": self.surah_id,
            "ayah_no": self.ayah_no,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        } 