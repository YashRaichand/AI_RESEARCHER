import uuid
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.users import User
from app.models.papers import Paper
from app.models.literature_reviews import LiteratureReview
from app.models.research_ideas import ResearchIdea
from app.models.knowledge_graphs import KnowledgeGraph
from app.models.flashcards import Flashcard
from app.models.presentations import Presentation
from app.models.reports import Report
from app.ml.citation_generator import CitationGenerator
from app.ml.lit_review_engine import LiteratureReviewEngine
from app.ml.intelligence_engines import (
    ResearchGapDetector, PaperComparisonEngine,
    KnowledgeGraphBuilder, ResearchIdeaGenerator, FlashcardGenerator,
)
from app.ml.slide_generator import SlideGenerator

# ── Citations ──────────────────────────────────────────────────────────────
citations_router = APIRouter(prefix="/citations", tags=["Citations"])
_citation_gen = CitationGenerator()


class CitationRequest(BaseModel):
    paper_id: str
    formats: Optional[List[str]] = None


@citations_router.post("/generate")
async def generate_citation(data: CitationRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Paper).where(Paper.id == data.paper_id, Paper.user_id == current_user.id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(404, "Paper not found")
    meta = {
        "title": paper.title,
        "authors": paper.authors or [],
        "year": str(paper.created_at.year) if paper.created_at else "2024",
        "journal": "",
        "doi": "",
    }
    return _citation_gen.generate_all(meta)


# ── Literature Review ──────────────────────────────────────────────────────
lit_router = APIRouter(prefix="/literature-review", tags=["Literature Review"])
_lit_engine = LiteratureReviewEngine()


class LitReviewRequest(BaseModel):
    topic: str
    paper_ids: List[str]


@lit_router.post("/generate")
async def generate_literature_review(data: LitReviewRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Paper).where(Paper.id.in_(data.paper_ids), Paper.user_id == current_user.id))
    papers = result.scalars().all()
    if not papers:
        raise HTTPException(404, "No papers found")
    context = "\n\n".join([f"Title: {p.title}\nAbstract: {p.abstract or ''}" for p in papers[:10]])
    review_data = _lit_engine.generate(data.topic, context)

    review = LiteratureReview(
        id=uuid.uuid4(), user_id=current_user.id, topic=data.topic,
        paper_ids=data.paper_ids, content=review_data["content"],
        themes=review_data["themes"], trends=review_data["trends"],
        key_papers=[p.title for p in papers[:5]], gaps=review_data["gaps"],
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return {"id": str(review.id), "topic": review.topic, "content": review.content,
            "themes": review.themes, "trends": review.trends, "gaps": review.gaps}


@lit_router.get("/")
async def list_reviews(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(LiteratureReview).where(LiteratureReview.user_id == current_user.id).order_by(LiteratureReview.created_at.desc()))
    reviews = result.scalars().all()
    return [{"id": str(r.id), "topic": r.topic, "created_at": str(r.created_at)} for r in reviews]


# ── Research Gaps ──────────────────────────────────────────────────────────
gaps_router = APIRouter(prefix="/gaps", tags=["Research Gaps"])
_gap_detector = ResearchGapDetector()


class GapsRequest(BaseModel):
    paper_ids: List[str]


@gaps_router.post("/detect")
async def detect_gaps(data: GapsRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Paper).where(Paper.id.in_(data.paper_ids), Paper.user_id == current_user.id))
    papers = result.scalars().all()
    context = "\n\n".join([f"Title: {p.title}\nAbstract: {p.abstract or ''}\nTopic: {p.topic}" for p in papers[:10]])
    gaps = _gap_detector.detect(context)
    return {"gaps": gaps, "paper_count": len(papers)}


# ── Paper Comparison ───────────────────────────────────────────────────────
compare_router = APIRouter(prefix="/compare", tags=["Comparison"])
_comparison_engine = PaperComparisonEngine()


class CompareRequest(BaseModel):
    paper_ids: List[str]


@compare_router.post("/")
async def compare_papers(data: CompareRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if len(data.paper_ids) < 2:
        raise HTTPException(400, "Need at least 2 papers to compare")
    result = await db.execute(select(Paper).where(Paper.id.in_(data.paper_ids), Paper.user_id == current_user.id))
    papers = result.scalars().all()
    papers_data = [{"id": str(p.id), "title": p.title, "abstract": p.abstract, "topic": p.topic} for p in papers]
    comparison = _comparison_engine.compare(papers_data)

    report = Report(
        id=uuid.uuid4(), user_id=current_user.id, paper_ids=data.paper_ids,
        report_type="comparison", title=f"Comparison of {len(papers)} papers",
        content=comparison.get("summary", ""), comparison_table=comparison.get("comparison_table"),
    )
    db.add(report)
    await db.commit()
    return comparison


# ── Knowledge Graph ────────────────────────────────────────────────────────
graph_router = APIRouter(prefix="/knowledge-graph", tags=["Knowledge Graph"])
_graph_builder = KnowledgeGraphBuilder()


class GraphRequest(BaseModel):
    paper_ids: List[str]
    title: Optional[str] = "Knowledge Graph"


@graph_router.post("/build")
async def build_graph(data: GraphRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Paper).where(Paper.id.in_(data.paper_ids), Paper.user_id == current_user.id))
    papers = result.scalars().all()
    papers_data = [{"id": str(p.id), "title": p.title, "authors": p.authors, "topic": p.topic, "keywords": p.keywords} for p in papers]
    graph_data = _graph_builder.build(papers_data)

    graph = KnowledgeGraph(
        id=uuid.uuid4(), user_id=current_user.id, paper_ids=data.paper_ids,
        title=data.title, nodes=graph_data["nodes"], edges=graph_data["edges"],
    )
    db.add(graph)
    await db.commit()
    await db.refresh(graph)
    return {"id": str(graph.id), "title": graph.title, "nodes": graph.nodes, "edges": graph.edges}


@graph_router.get("/")
async def list_graphs(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(KnowledgeGraph).where(KnowledgeGraph.user_id == current_user.id).order_by(KnowledgeGraph.created_at.desc()))
    graphs = result.scalars().all()
    return [{"id": str(g.id), "title": g.title, "created_at": str(g.created_at)} for g in graphs]


# ── Research Ideas ─────────────────────────────────────────────────────────
ideas_router = APIRouter(prefix="/ideas", tags=["Research Ideas"])
_idea_gen = ResearchIdeaGenerator()


class IdeasRequest(BaseModel):
    paper_ids: List[str]


@ideas_router.post("/generate")
async def generate_ideas(data: IdeasRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Paper).where(Paper.id.in_(data.paper_ids), Paper.user_id == current_user.id))
    papers = result.scalars().all()
    context = "\n\n".join([f"Title: {p.title}\nAbstract: {p.abstract or ''}" for p in papers[:8]])
    ideas = _idea_gen.generate(context)

    saved = []
    for idea in ideas[:8]:
        r_idea = ResearchIdea(
            id=uuid.uuid4(), user_id=current_user.id, paper_ids=data.paper_ids,
            title=idea.get("title", "Research Idea"),
            description=idea.get("description", ""),
            rationale=idea.get("rationale", ""),
            difficulty=idea.get("difficulty", "medium"),
            novelty_score=idea.get("novelty_score", 50),
            related_papers=[p.title for p in papers[:3]],
        )
        db.add(r_idea)
        saved.append(idea)
    await db.commit()
    return {"ideas": saved}


@ideas_router.get("/")
async def list_ideas(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(ResearchIdea).where(ResearchIdea.user_id == current_user.id).order_by(ResearchIdea.created_at.desc()))
    ideas = result.scalars().all()
    return [{"id": str(i.id), "title": i.title, "difficulty": i.difficulty, "novelty_score": i.novelty_score} for i in ideas]


# ── Flashcards ─────────────────────────────────────────────────────────────
flashcards_router = APIRouter(prefix="/flashcards", tags=["Flashcards"])
_flashcard_gen = FlashcardGenerator()


class FlashcardsRequest(BaseModel):
    paper_id: str


@flashcards_router.post("/generate")
async def generate_flashcards(data: FlashcardsRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Paper).where(Paper.id == data.paper_id, Paper.user_id == current_user.id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(404, "Paper not found")
    paper_data = {"title": paper.title, "abstract": paper.abstract, "parsed_sections": paper.parsed_sections}
    cards = _flashcard_gen.generate(paper_data)

    saved = []
    for card in cards:
        fc = Flashcard(
            id=uuid.uuid4(), user_id=current_user.id, paper_id=paper.id,
            front=card.get("front", ""), back=card.get("back", ""),
            card_type=card.get("card_type", "qa"),
            difficulty=card.get("difficulty", "medium"),
            topic=card.get("topic", paper.topic),
        )
        db.add(fc)
        saved.append(card)
    await db.commit()
    return {"flashcards": saved, "count": len(saved)}


@flashcards_router.get("/")
async def list_flashcards(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Flashcard).where(Flashcard.user_id == current_user.id).order_by(Flashcard.created_at.desc()))
    cards = result.scalars().all()
    return [{"id": str(c.id), "front": c.front, "back": c.back, "card_type": c.card_type, "difficulty": c.difficulty, "is_learned": c.is_learned} for c in cards]


@flashcards_router.patch("/{card_id}/learned")
async def mark_learned(card_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Flashcard).where(Flashcard.id == card_id, Flashcard.user_id == current_user.id))
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(404, "Flashcard not found")
    card.is_learned = not card.is_learned
    await db.commit()
    return {"id": card_id, "is_learned": card.is_learned}


# ── Slides ─────────────────────────────────────────────────────────────────
slides_router = APIRouter(prefix="/slides", tags=["Slides"])
_slide_gen = SlideGenerator()


class SlidesRequest(BaseModel):
    paper_ids: List[str]
    title: Optional[str] = "Research Presentation"


@slides_router.post("/generate")
async def generate_slides(data: SlidesRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Paper).where(Paper.id.in_(data.paper_ids), Paper.user_id == current_user.id))
    papers = result.scalars().all()
    if not papers:
        raise HTTPException(404, "No papers found")
    papers_data = [{"id": str(p.id), "title": p.title, "abstract": p.abstract, "authors": p.authors, "keywords": p.keywords, "topic": p.topic, "quality_score": p.quality_score} for p in papers]
    pptx_bytes = _slide_gen.generate(papers_data, data.title)

    presentation = Presentation(
        id=uuid.uuid4(), user_id=current_user.id, paper_ids=data.paper_ids,
        title=data.title, slide_count=len(papers) + 4, slides_data=[],
    )
    db.add(presentation)
    await db.commit()

    return Response(
        content=pptx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{data.title}.pptx"'},
    )
