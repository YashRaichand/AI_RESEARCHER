import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
from app.core.database import Base

class Presentation(Base):
    __tablename__ = "presentations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    paper_ids: Mapped[list] = mapped_column(JSON, default=list)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slide_count: Mapped[int] = mapped_column(Integer, default=0)
    file_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    slides_data: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="presentations")
