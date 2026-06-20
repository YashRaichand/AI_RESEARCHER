from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
import uuid


class PaperOut(BaseModel):
    id: uuid.UUID
    title: str
    authors: List[Any] = []
    abstract: Optional[str] = None
    keywords: List[str] = []
    file_url: Optional[str] = None
    file_type: str
    status: str
    topic: str
    quality_score: Optional[float] = None
    impact_score: Optional[float] = None
    page_count: int = 0
    word_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class PaperList(BaseModel):
    papers: List[PaperOut]
    total: int
    page: int
    per_page: int


class PaperStatus(BaseModel):
    id: uuid.UUID
    status: str
    processing_error: Optional[str] = None
