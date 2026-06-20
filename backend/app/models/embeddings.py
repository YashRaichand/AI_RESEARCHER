import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ChunkType(str, enum.Enum):
    full_paper = "full_paper"
    section = "section"
    paragraph = "paragraph"
    table = "table"
    figure_caption = "figure_caption"


class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paper_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_type: Mapped[ChunkType] = mapped_column(SAEnum(ChunkType), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    section_name: Mapped[str] = mapped_column(String(255), nullable=True)
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False)
    faiss_index_id: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="embeddings")
