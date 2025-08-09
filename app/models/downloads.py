import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.extensions import db


class DownloadStatus(str, Enum):
    """Download status enumeration."""
    QUEUED = "queued"
    READY = "ready"
    FAILED = "failed"


class Download(db.Model):
    """User downloads for offline access."""
    
    __tablename__ = "downloads"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    reciter_id = Column(Integer, ForeignKey("reciters.id"), primary_key=True)
    surah_id = Column(Integer, primary_key=True)
    status = Column(String(20), nullable=False, default=DownloadStatus.QUEUED)
    bytes = Column(Integer, nullable=True)  # File size in bytes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="downloads")
    reciter = relationship("Reciter", back_populates="downloads")
    
    __table_args__ = (
        UniqueConstraint("user_id", "reciter_id", "surah_id", name="uq_downloads_user_reciter_surah"),
    )
    
    def __repr__(self):
        return f"<Download(user_id={self.user_id}, reciter_id={self.reciter_id}, surah_id={self.surah_id}, status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """Convert download to dictionary for API responses."""
        return {
            "user_id": str(self.user_id),
            "reciter_id": self.reciter_id,
            "surah_id": self.surah_id,
            "status": self.status,
            "bytes": self.bytes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @property
    def is_ready(self) -> bool:
        """Check if download is ready."""
        return self.status == DownloadStatus.READY
    
    @property
    def is_failed(self) -> bool:
        """Check if download failed."""
        return self.status == DownloadStatus.FAILED
    
    @property
    def is_queued(self) -> bool:
        """Check if download is queued."""
        return self.status == DownloadStatus.QUEUED 