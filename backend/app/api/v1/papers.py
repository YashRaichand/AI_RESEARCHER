import uuid
import os
import tempfile
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import cloudinary
import cloudinary.uploader
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import get_settings
from app.models.users import User
from app.models.papers import Paper, PaperStatus, FileType
from app.schemas.papers import PaperOut, PaperList
from app.tasks.paper_tasks import process_paper_task

settings = get_settings()
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

router = APIRouter(prefix="/papers", tags=["Papers"])

ALLOWED_TYPES = {"application/pdf": "pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx", "text/plain": "txt"}
MAX_SIZE = settings.MAX_FILE_SIZE_MB * 1024 * 1024


@router.post("/upload", response_model=PaperOut)
async def upload_paper(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content_type = file.content_type or ""
    file_type_str = ALLOWED_TYPES.get(content_type)
    if not file_type_str:
        ext = (file.filename or "").rsplit(".", 1)[-1].lower()
        file_type_str = ext if ext in ["pdf", "docx", "txt"] else None
    if not file_type_str:
        raise HTTPException(400, "Unsupported file type. Upload PDF, DOCX, or TXT.")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(400, f"File too large. Max {settings.MAX_FILE_SIZE_MB}MB.")

    file_url = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type_str}") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        if settings.CLOUDINARY_CLOUD_NAME:
            upload_result = cloudinary.uploader.upload(
                tmp_path, resource_type="raw",
                folder="scientia/papers",
                public_id=f"{uuid.uuid4()}_{file.filename}",
            )
            file_url = upload_result.get("secure_url", "")
    except Exception:
        file_url = f"local://{tmp_path}"

    paper = Paper(
        id=uuid.uuid4(),
        user_id=current_user.id,
        title=file.filename or "Untitled",
        file_url=file_url,
        file_type=FileType(file_type_str),
        status=PaperStatus.pending,
    )
    db.add(paper)
    await db.commit()
    await db.refresh(paper)

    process_paper_task.delay(str(paper.id), tmp_path, file_type_str)

    return PaperOut.model_validate(paper)


@router.get("/", response_model=PaperList)
async def list_papers(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    topic: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Paper).where(Paper.user_id == current_user.id)
    if topic:
        query = query.where(Paper.topic == topic)
    if status:
        query = query.where(Paper.status == status)
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    query = query.offset((page - 1) * per_page).limit(per_page).order_by(Paper.created_at.desc())
    result = await db.execute(query)
    papers = result.scalars().all()
    return PaperList(papers=[PaperOut.model_validate(p) for p in papers], total=total, page=page, per_page=per_page)


@router.get("/{paper_id}", response_model=PaperOut)
async def get_paper(paper_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(404, "Paper not found")
    return PaperOut.model_validate(paper)


@router.delete("/{paper_id}")
async def delete_paper(paper_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(404, "Paper not found")
    await db.delete(paper)
    await db.commit()
    return {"message": "Paper deleted"}


@router.get("/{paper_id}/status")
async def get_paper_status(paper_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(404, "Paper not found")
    return {"id": str(paper.id), "status": paper.status, "processing_error": paper.processing_error}
