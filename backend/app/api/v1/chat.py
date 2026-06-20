import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.users import User
from app.models.chats import ChatSession, ChatMessage, MessageRole
from app.ml.embedding_engine import EmbeddingEngine
from app.ml.rag_engine import RAGEngine
from app.ml.chat_engine import ChatEngine

router = APIRouter(prefix="/chat", tags=["Chat"])

_embedding_engine = None
_rag_engine = None
_chat_engine = None


def get_chat_engine():
    global _embedding_engine, _rag_engine, _chat_engine
    if _chat_engine is None:
        _embedding_engine = EmbeddingEngine()
        _rag_engine = RAGEngine(_embedding_engine)
        _chat_engine = ChatEngine(_rag_engine)
    return _chat_engine


class CreateSessionRequest(BaseModel):
    paper_ids: List[str]
    title: Optional[str] = "New Chat"


class MessageRequest(BaseModel):
    question: str


@router.post("/sessions")
async def create_session(
    data: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = ChatSession(
        id=uuid.uuid4(),
        user_id=current_user.id,
        title=data.title,
        paper_ids=data.paper_ids,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {
        "id": str(session.id),
        "title": session.title,
        "paper_ids": session.paper_ids,
        "created_at": str(session.created_at),
    }


@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .limit(50)
    )
    sessions = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "title": s.title,
            "paper_ids": s.paper_ids,
            "created_at": str(s.created_at),
        }
        for s in sessions
    ]


@router.post("/sessions/{session_id}/message")
async def send_message(
    session_id: str,
    data: MessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")

    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
    )
    history = [
        {"role": m.role, "content": m.content}
        for m in reversed(history_result.scalars().all())
    ]

    user_msg = ChatMessage(
        id=uuid.uuid4(),
        session_id=session.id,
        role=MessageRole.user,
        content=data.question,
        citations=[],
    )
    db.add(user_msg)
    await db.commit()

    async def stream_response():
        full_response = ""
        citations = []
        engine = get_chat_engine()
        try:
            async for chunk in engine.chat(
                data.question,
                paper_ids=session.paper_ids,
                chat_history=history,
            ):
                if "__CITATIONS__" in chunk:
                    text_part, citations = engine.extract_citations_from_response(chunk)
                    if text_part:
                        full_response += text_part
                        yield f"data: {json.dumps({'type': 'chunk', 'content': text_part})}\n\n"
                else:
                    full_response += chunk
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

            yield f"data: {json.dumps({'type': 'citations', 'sources': citations})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as save_db:
                assistant_msg = ChatMessage(
                    id=uuid.uuid4(),
                    session_id=session.id,
                    role=MessageRole.assistant,
                    content=full_response,
                    citations=citations,
                )
                save_db.add(assistant_msg)
                await save_db.commit()

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")


@router.get("/sessions/{session_id}/history")
async def get_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")

    msgs = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    messages = msgs.scalars().all()
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "citations": m.citations,
                "created_at": str(m.created_at),
            }
            for m in messages
        ],
    }
