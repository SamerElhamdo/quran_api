from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class ProgressSchema(BaseModel):
    """User progress schema."""
    
    user_id: str = Field(description="User's unique identifier")
    surah_id: int = Field(description="Surah number", ge=1, le=114)
    ayah_no: int = Field(description="Ayah number within surah", ge=1)
    ef: float = Field(description="Easiness factor", ge=1.3, le=2.5)
    interval_days: int = Field(description="Days until next review", ge=0)
    due: date = Field(description="Due date for review")
    lapses: int = Field(description="Number of failures", ge=0)
    updated_at: str = Field(description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ReviewItemSchema(BaseModel):
    """Review queue item schema."""
    
    id: str = Field(description="Review queue item ID")
    surah_id: int = Field(description="Surah number", ge=1, le=114)
    ayah_no: int = Field(description="Ayah number within surah", ge=1)
    due: date = Field(description="Due date for review")
    ef: float = Field(description="Current easiness factor", ge=1.3, le=2.5)
    interval_days: int = Field(description="Current interval in days", ge=0)
    created_at: str = Field(description="Creation timestamp")
    
    class Config:
        from_attributes = True


class GradeItemSchema(BaseModel):
    """Individual grade item schema."""
    
    surah_id: int = Field(description="Surah number", ge=1, le=114)
    ayah_no: int = Field(description="Ayah number within surah", ge=1)
    q: int = Field(description="Grade (0-3)", ge=0, le=3)
    
    class Config:
        json_schema_extra = {
            "example": {
                "surah_id": 1,
                "ayah_no": 1,
                "q": 3
            }
        }


class GradeRequestSchema(BaseModel):
    """Grade request schema."""
    
    items: List[GradeItemSchema] = Field(
        description="List of items to grade",
        min_items=1,
        max_items=100
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {"surah_id": 1, "ayah_no": 1, "q": 3},
                    {"surah_id": 1, "ayah_no": 2, "q": 2}
                ]
            }
        }


class GradeResponseSchema(BaseModel):
    """Grade response schema."""
    
    updated_count: int = Field(description="Number of items updated")
    next_review_date: Optional[date] = Field(description="Next review date")
    summary: List[dict] = Field(description="Summary of updates")
    
    class Config:
        json_schema_extra = {
            "example": {
                "updated_count": 2,
                "next_review_date": "2024-01-15",
                "summary": [
                    {"surah_id": 1, "ayah_no": 1, "new_ef": 2.6, "new_interval": 1},
                    {"surah_id": 1, "ayah_no": 2, "new_ef": 2.3, "new_interval": 0}
                ]
            }
        }


class ProgressResetSchema(BaseModel):
    """Progress reset request schema."""
    
    surah_id: int = Field(description="Surah number", ge=1, le=114)
    from_ayah: int = Field(description="Starting ayah number", ge=1)
    to_ayah: int = Field(description="Ending ayah number", ge=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "surah_id": 1,
                "from_ayah": 1,
                "to_ayah": 7
            }
        } 