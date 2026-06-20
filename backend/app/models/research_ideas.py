import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Text, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
from app.core.database import Base


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class ResearchIdea(Base):
    __tablename__ = "research_ideas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    paper_ids: Mapped[list] = mapped_column(JSON, default=list)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=True)
    difficulty: Mapped[Difficulty] = mapped_column(SAEnum(Difficulty), default=Difficulty.medium)
    novelty_score: Mapped[float] = mapped_column(Float, default=0.0)
    related_papers: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="research_ideas")
