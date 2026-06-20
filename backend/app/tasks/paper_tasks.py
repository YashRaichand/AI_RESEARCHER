import asyncio
import uuid
from app.workers.celery_app import celery_app
from app.ml.pdf_engine import PDFEngine
from app.ml.paper_parser import ScientificPaperParser
from app.ml.embedding_engine import EmbeddingEngine
from app.ml.intelligence_engines import ResearchGapDetector
import structlog

logger = structlog.get_logger()
pdf_engine = PDFEngine()
parser = ScientificPaperParser()
embedding_engine = EmbeddingEngine()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_paper_task(self, paper_id: str, file_path: str, file_type: str):
    try:
        logger.info("processing_paper", paper_id=paper_id, file_type=file_type)
        _update_paper_status(paper_id, "processing")

        paper_data = pdf_engine.extract(file_path, file_type)
        parsed = parser.parse(paper_data.get("full_text", ""))
        paper_data["parsed_sections"] = parsed["sections"]

        embeddings_stored = embedding_engine.embed_paper(paper_data, paper_id)

        _save_paper_results(paper_id, paper_data, embeddings_stored)
        _update_paper_status(paper_id, "completed")
        logger.info("paper_processed", paper_id=paper_id, chunks=len(embeddings_stored))
        return {"status": "completed", "paper_id": paper_id, "chunks": len(embeddings_stored)}

    except Exception as exc:
        logger.error("paper_processing_failed", paper_id=paper_id, error=str(exc))
        _update_paper_status(paper_id, "failed", error=str(exc))
        raise self.retry(exc=exc)


def _update_paper_status(paper_id: str, status: str, error: str = None):
    from sqlalchemy import create_engine, text
    from app.core.config import get_settings
    settings = get_settings()
    sync_url = settings.DATABASE_URL.replace("+asyncpg", "").replace("postgresql+asyncpg", "postgresql")
    try:
        engine = create_engine(sync_url)
        with engine.connect() as conn:
            if error:
                conn.execute(text(
                    "UPDATE papers SET status=:status, processing_error=:error WHERE id=:id"
                ), {"status": status, "error": error, "id": paper_id})
            else:
                conn.execute(text("UPDATE papers SET status=:status WHERE id=:id"), {"status": status, "id": paper_id})
            conn.commit()
    except Exception as e:
        logger.error("db_update_failed", error=str(e))


def _save_paper_results(paper_id: str, paper_data: dict, embeddings: list):
    from sqlalchemy import create_engine, text
    from app.core.config import get_settings
    import json
    settings = get_settings()
    sync_url = settings.DATABASE_URL.replace("+asyncpg", "").replace("postgresql+asyncpg", "postgresql")
    try:
        engine = create_engine(sync_url)
        with engine.connect() as conn:
            conn.execute(text("""
                UPDATE papers SET
                    title=:title, abstract=:abstract, keywords=:keywords,
                    parsed_sections=:sections, references=:refs,
                    figures=:figures, tables=:tables, equations=:equations,
                    page_count=:pages, word_count=:words
                WHERE id=:id
            """), {
                "title": paper_data.get("title", "Untitled")[:500],
                "abstract": paper_data.get("abstract", "")[:5000],
                "keywords": json.dumps(paper_data.get("keywords", [])),
                "sections": json.dumps({k: v[:2000] for k, v in paper_data.get("parsed_sections", {}).items()}),
                "refs": json.dumps(paper_data.get("references", [])[:50]),
                "figures": json.dumps(paper_data.get("figures", [])[:30]),
                "tables": json.dumps(paper_data.get("tables", [])[:30]),
                "equations": json.dumps(paper_data.get("equations", [])[:50]),
                "pages": paper_data.get("page_count", 0),
                "words": paper_data.get("word_count", 0),
                "id": paper_id,
            })
            for emb in embeddings[:200]:
                conn.execute(text("""
                    INSERT INTO embeddings (id, paper_id, chunk_type, chunk_text, chunk_index, section_name, embedding_model, faiss_index_id)
                    VALUES (:id, :paper_id, :chunk_type, :chunk_text, :chunk_index, :section_name, :model, :faiss_id)
                    ON CONFLICT DO NOTHING
                """), {
                    "id": str(uuid.uuid4()),
                    "paper_id": paper_id,
                    "chunk_type": emb.get("chunk_type", "paragraph"),
                    "chunk_text": emb.get("chunk_text", "")[:5000],
                    "chunk_index": emb.get("chunk_index", 0),
                    "section_name": emb.get("section_name", ""),
                    "model": emb.get("embedding_model", "all-mpnet-base-v2"),
                    "faiss_id": emb.get("faiss_index_id", 0),
                })
            conn.commit()
    except Exception as e:
        logger.error("save_results_failed", error=str(e))
