from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db


class Surah(db.Model):
    """Quran surah model."""
    
    __tablename__ = "surahs"
    
    id = Column(Integer, primary_key=True, autoincrement=False)  # Use surah number as ID
    name_arabic = Column(String(255), nullable=False)
    name_english = Column(String(255), nullable=False)
    total_ayahs = Column(Integer, nullable=False)
    revelation_type = Column(String(50), nullable=False)  # Meccan or Medinan
    juz = Column(Integer, nullable=False)
    
    # Relationships
    ayahs = relationship("AyahIndex", back_populates="surah", lazy="dynamic")
    
    def __repr__(self):
        return f"<Surah(id={self.id}, name_arabic='{self.name_arabic}')>"
    
    def to_dict(self) -> dict:
        """Convert surah to dictionary for API responses."""
        return {
            "id": self.id,
            "name_arabic": self.name_arabic,
            "name_english": self.name_english,
            "total_ayahs": self.total_ayahs,
            "revelation_type": self.revelation_type,
            "juz": self.juz,
        }


class Reciter(db.Model):
    """Quran reciter model."""
    
    __tablename__ = "reciters"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    bitrate_kbps = Column(Integer, nullable=False)
    base_url = Column(String(500), nullable=False)
    
    # Relationships
    user_settings = relationship("UserSettings", back_populates="reciter")
    downloads = relationship("Download", back_populates="reciter")
    
    def __repr__(self):
        return f"<Reciter(id={self.id}, code='{self.code}', name='{self.name}')>"
    
    def to_dict(self) -> dict:
        """Convert reciter to dictionary for API responses."""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "bitrate_kbps": self.bitrate_kbps,
            "base_url": self.base_url,
        }


class AyahIndex(db.Model):
    """Search index for Quran verses (optional)."""
    
    __tablename__ = "ayah_index"
    
    surah_id = Column(Integer, ForeignKey('surahs.id'), primary_key=True)
    ayah_no = Column(Integer, primary_key=True)
    text_plain = Column(Text, nullable=False)  # Text without diacritics
    page = Column(Integer, nullable=False)
    
    # Relationships
    surah = relationship("Surah", back_populates="ayahs")
    
    def __repr__(self):
        return f"<AyahIndex(surah_id={self.surah_id}, ayah_no={self.ayah_no})>"
    
    def to_dict(self) -> dict:
        """Convert ayah index to dictionary for API responses."""
        return {
            "surah_id": self.surah_id,
            "ayah_no": self.ayah_no,
            "text_plain": self.text_plain,
            "page": self.page,
        } 