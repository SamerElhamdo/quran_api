import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.extensions import db


class Playlist(db.Model):
    """User playlist for Quran verses."""
    
    __tablename__ = "playlists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="playlists")
    items = relationship("PlaylistItem", back_populates="playlist", cascade="all, delete-orphan", order_by="PlaylistItem.position")
    
    def __repr__(self):
        return f"<Playlist(id={self.id}, title='{self.title}', user_id={self.user_id})>"
    
    def to_dict(self) -> dict:
        """Convert playlist to dictionary for API responses."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "items": [item.to_dict() for item in self.items],
        }


class PlaylistItem(db.Model):
    """Individual item in a playlist."""
    
    __tablename__ = "playlist_items"
    
    playlist_id = Column(UUID(as_uuid=True), ForeignKey("playlists.id"), primary_key=True)
    position = Column(Integer, primary_key=True)
    from_surah = Column(Integer, nullable=False)
    from_ayah = Column(Integer, nullable=False)
    to_surah = Column(Integer, nullable=False)
    to_ayah = Column(Integer, nullable=False)
    repeat = Column(Integer, nullable=False, default=3)
    speed = Column(Numeric(3, 2), nullable=False, default=1.0)
    
    # Relationships
    playlist = relationship("Playlist", back_populates="items")
    
    __table_args__ = (
        UniqueConstraint("playlist_id", "position", name="uq_playlist_item_playlist_position"),
    )
    
    def __repr__(self):
        return f"<PlaylistItem(playlist_id={self.playlist_id}, position={self.position}, from_surah={self.from_surah}, from_ayah={self.from_ayah})>"
    
    def to_dict(self) -> dict:
        """Convert playlist item to dictionary for API responses."""
        return {
            "playlist_id": str(self.playlist_id),
            "position": self.position,
            "from_surah": self.from_surah,
            "from_ayah": self.from_ayah,
            "to_surah": self.to_surah,
            "to_ayah": self.to_ayah,
            "repeat": self.repeat,
            "speed": float(self.speed) if self.speed else 1.0,
        } 