import sys
import traceback

try:
    import redis.asyncio as aioredis
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from contextlib import asynccontextmanager
    from app.core.config import get_settings
    from app.core.database import check_db_connection

    settings = get_settings()
    _redis_client = None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        global _redis_client
        try:
            _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as e:
            print(f"Redis connection failed: {e}", flush=True)
        yield
        if _redis_client:
            await _redis_client.aclose()

    app = FastAPI(
        title="Scientia AI",
        version="1.0.0",
        description="Advanced AI Research Assistant for Scientific Papers",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.api.v1.auth import router as auth_router
    from app.api.v1.papers import router as papers_router
    from app.api.v1.chat import router as chat_router
    from app.api.v1.intelligence import (
        citations_router, lit_router, gaps_router, compare_router,
        graph_router, ideas_router, flashcards_router, slides_router,
    )

    PREFIX = "/api/v1"
    app.include_router(auth_router, prefix=PREFIX)
    app.include_router(papers_router, prefix=PREFIX)
    app.include_router(chat_router, prefix=PREFIX)
    app.include_router(citations_router, prefix=PREFIX)
    app.include_router(lit_router, prefix=PREFIX)
    app.include_router(gaps_router, prefix=PREFIX)
    app.include_router(compare_router, prefix=PREFIX)
    app.include_router(graph_router, prefix=PREFIX)
    app.include_router(ideas_router, prefix=PREFIX)
    app.include_router(flashcards_router, prefix=PREFIX)
    app.include_router(slides_router, prefix=PREFIX)

    @app.get("/health")
    async def health():
        db_ok = await check_db_connection()
        redis_ok = False
        try:
            if _redis_client:
                await _redis_client.ping()
                redis_ok = True
        except Exception:
            pass
        return {
            "status": "healthy" if db_ok else "degraded",
            "db": "connected" if db_ok else "disconnected",
            "redis": "connected" if redis_ok else "disconnected",
            "version": "1.0.0",
        }

    @app.get("/")
    async def root():
        return {"message": "Scientia AI API", "docs": "/docs", "version": "1.0.0"}

    print("App loaded successfully", flush=True)

except Exception as e:
    print(f"STARTUP ERROR: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)