# Scientia AI

**Advanced AI Research Assistant for Scientific Papers**

Upload PDFs, ask questions across papers, generate literature reviews, detect research gaps, build knowledge graphs, create presentations, and generate flashcards — all powered by AI.

---

## Features

- **PDF/DOCX/TXT ingestion** — extract text, tables, figures, equations automatically
- **Multi-paper RAG chat** — ask questions across 100+ papers with grounded citations
- **Literature review generator** — structured academic reviews with themes and gaps
- **Research gap detector** — find underexplored topics with novelty scores
- **Paper comparison** — side-by-side comparison tables
- **Knowledge graph** — interactive visualization of paper relationships
- **Research idea generator** — novel directions from discovered gaps
- **Flashcard generator** — Q&A, revision, and exam cards with flip animation
- **Presentation builder** — auto-generate PPTX from selected papers
- **Citation generator** — APA, MLA, IEEE, Chicago, BibTeX

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI, Python 3.11 |
| Frontend | Next.js 15, TypeScript, TailwindCSS |
| ML/NLP | Sentence Transformers, FAISS, LangChain, Anthropic |
| Database | PostgreSQL 15 |
| Cache/Queue | Redis 7, Celery |
| Storage | Cloudinary |
| Deployment | Docker, Render |
| CI/CD | GitHub Actions |

---

## Quick Start (Docker)

```bash
# 1. Clone and enter
git clone https://github.com/youruser/scientia-ai.git
cd scientia-ai

# 2. Copy env file and fill in your keys
cp .env.example .env
# Edit .env — set ANTHROPIC_API_KEY, CLOUDINARY_*, GOOGLE_* at minimum

# 3. Start everything
docker-compose up --build

# 4. Run database migrations
docker-compose exec backend alembic upgrade head
```

Open `http://localhost:3000` for the frontend and `http://localhost:8000/docs` for the API.

---

## Local Development (no Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env       # fill in values

# Start PostgreSQL and Redis locally, then:
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# In a separate terminal, start Celery worker:
celery -A app.workers.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
npm run dev
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `REDIS_URL` | ✅ | Redis connection string |
| `SECRET_KEY` | ✅ | JWT signing secret (min 32 chars) |
| `ANTHROPIC_API_KEY` | ✅ | For AI chat, literature review, etc. |
| `CLOUDINARY_CLOUD_NAME` | ✅ | File storage |
| `CLOUDINARY_API_KEY` | ✅ | File storage |
| `CLOUDINARY_API_SECRET` | ✅ | File storage |
| `GOOGLE_CLIENT_ID` | Optional | Google OAuth login |
| `GOOGLE_CLIENT_SECRET` | Optional | Google OAuth login |

---

## Deploy on Render

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for full step-by-step instructions.

**Quick version:**
1. Fork this repo to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect your repo — Render auto-reads `render.yaml`
4. Set the secret environment variables in the Render dashboard
5. Click Deploy

---

## API Documentation

Visit `http://localhost:8000/docs` for the interactive Swagger UI covering all endpoints:

- `POST /api/v1/auth/register` — create account
- `POST /api/v1/auth/login` — get JWT tokens
- `POST /api/v1/papers/upload` — upload a paper
- `GET /api/v1/papers/` — list papers
- `POST /api/v1/chat/sessions` — start chat session
- `POST /api/v1/chat/sessions/{id}/message` — stream AI response
- `POST /api/v1/literature-review/generate` — generate lit review
- `POST /api/v1/gaps/detect` — detect research gaps
- `POST /api/v1/compare/` — compare papers
- `POST /api/v1/knowledge-graph/build` — build knowledge graph
- `POST /api/v1/ideas/generate` — generate research ideas
- `POST /api/v1/flashcards/generate` — generate flashcards
- `POST /api/v1/slides/generate` — generate PPTX

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## Project Structure

```
scientia-ai/
├── backend/
│   ├── app/
│   │   ├── api/v1/         # FastAPI routers
│   │   ├── core/           # config, database, security
│   │   ├── ml/             # PDF engine, RAG, chat, citations, etc.
│   │   ├── models/         # SQLAlchemy models (12 tables)
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── tasks/          # Celery tasks
│   │   └── workers/        # Celery app
│   ├── alembic/            # DB migrations
│   ├── tests/              # pytest tests
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js 15 App Router pages
│   │   ├── components/     # GlassCard, DashboardShell, etc.
│   │   └── lib/            # API client, auth context, utils
│   └── Dockerfile
├── infra/
│   └── prometheus.yml
├── .github/workflows/ci.yml
├── docker-compose.yml
├── render.yaml
└── .env.example
```

---

## License

MIT
