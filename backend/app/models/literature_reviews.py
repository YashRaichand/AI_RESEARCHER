import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
from app.core.database import Base

class LiteratureReview(Base):
    __tablename__ = "literature_reviews"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    paper_ids: Mapped[list] = mapped_column(JSON, default=list)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    themes: Mapped[list] = mapped_column(JSON, default=list)
    trends: Mapped[list] = mapped_column(JSON, default=list)
    key_papers: Mapped[list] = mapped_column(JSON, default=list)
    gaps: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    user = relationship("User", back_populates="literature_reviews")
