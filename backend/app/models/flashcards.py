import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class CardType(str, enum.Enum):
    qa = "qa"
    revision = "revision"
    exam = "exam"

class CardDifficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class Flashcard(Base):
    __tablename__ = "flashcards"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    paper_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True)
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    card_type: Mapped[CardType] = mapped_column(SAEnum(CardType), default=CardType.qa)
    difficulty: Mapped[CardDifficulty] = mapped_column(SAEnum(CardDifficulty), default=CardDifficulty.medium)
    topic: Mapped[str] = mapped_column(String(255), nullable=True)
    is_learned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="flashcards")
    paper = relationship("Paper", back_populates="flashcards")
