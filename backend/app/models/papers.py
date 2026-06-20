import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Float, Integer, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
from app.core.database import Base


class FileType(str, enum.Enum):
    pdf = "pdf"
    docx = "docx"
    txt = "txt"


class PaperStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class PaperTopic(str, enum.Enum):
    nlp = "NLP"
    computer_vision = "Computer Vision"
    robotics = "Robotics"
    reinforcement_learning = "Reinforcement Learning"
    bioinformatics = "Bioinformatics"
    healthcare_ai = "Healthcare AI"
    finance_ai = "Finance AI"
    other = "Other"


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    authors: Mapped[list] = mapped_column(JSON, default=list)
    abstract: Mapped[str] = mapped_column(Text, nullable=True)
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    file_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    file_type: Mapped[FileType] = mapped_column(SAEnum(FileType), nullable=False)
    status: Mapped[PaperStatus] = mapped_column(SAEnum(PaperStatus), default=PaperStatus.pending, index=True)
    topic: Mapped[PaperTopic] = mapped_column(SAEnum(PaperTopic), default=PaperTopic.other, index=True)
    quality_score: Mapped[float] = mapped_column(Float, nullable=True)
    impact_score: Mapped[float] = mapped_column(Float, nullable=True)
    parsed_sections: Mapped[dict] = mapped_column(JSON, default=dict)
    references: Mapped[list] = mapped_column(JSON, default=list)
    figures: Mapped[list] = mapped_column(JSON, default=list)
    tables: Mapped[list] = mapped_column(JSON, default=list)
    equations: Mapped[list] = mapped_column(JSON, default=list)
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    processing_error: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="papers")
    paper_authors = relationship("Author", back_populates="paper", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="paper", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="paper", cascade="all, delete-orphan")
