import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.extensions import db


class UserRole(str, Enum):
    """User role enumeration."""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(db.Model):
    """User model for authentication and profile management."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_or_phone = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.STUDENT)
    locale = Column(String(10), nullable=False, default="ar")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    review_queue = relationship("ReviewQueue", back_populates="user", cascade="all, delete-orphan")
    playlists = relationship("Playlist", back_populates="user", cascade="all, delete-orphan")
    downloads = relationship("Download", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email_or_phone='{self.email_or_phone}', role='{self.role}')>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN
    
    @property
    def is_teacher(self) -> bool:
        """Check if user is teacher or admin."""
        return self.role in [UserRole.TEACHER, UserRole.ADMIN]
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for API responses."""
        return {
            "id": str(self.id),
            "email_or_phone": self.email_or_phone,
            "display_name": self.display_name,
            "role": self.role,
            "locale": self.locale,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserSettings(db.Model):
    """User preferences and settings."""
    
    __tablename__ = "user_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    reciter_id = Column(db.Integer, ForeignKey("reciters.id"), nullable=True)
    default_speed = Column(db.Numeric(3, 2), nullable=False, default=1.0)
    tajweed_enabled = Column(Boolean, nullable=False, default=True)
    font_scale = Column(db.Numeric(3, 2), nullable=False, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="settings")
    reciter = relationship("Reciter")
    
    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, reciter_id={self.reciter_id})>"
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary for API responses."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "reciter_id": self.reciter_id,
            "default_speed": float(self.default_speed) if self.default_speed else 1.0,
            "tajweed_enabled": self.tajweed_enabled,
            "font_scale": float(self.font_scale) if self.font_scale else 1.0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        } 