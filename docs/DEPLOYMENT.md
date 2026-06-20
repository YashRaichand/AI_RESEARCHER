# Deploying Scientia AI to Render

## Prerequisites
- GitHub account with this repo pushed
- Render account (free at render.com)
- Anthropic API key
- Cloudinary account (free tier works)

---

## Step 1 — Push to GitHub

```bash
cd scientia-ai
git init
git add .
git commit -m "Initial commit"
gh repo create scientia-ai --public --push
# or push manually to your GitHub
```

---

## Step 2 — Create a New Blueprint on Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **New** → **Blueprint**
3. Connect your GitHub account and select the `scientia-ai` repo
4. Render will detect `render.yaml` automatically
5. Click **Apply**

Render will create these services automatically:
- `scientia-backend` — FastAPI web service
- `scientia-frontend` — Next.js web service
- `scientia-celery-worker` — Celery background worker
- `scientia-postgres` — PostgreSQL database
- `scientia-redis` — Redis instance

---

## Step 3 — Set Secret Environment Variables

Some variables are marked `sync: false` in `render.yaml` — you must set these manually.

Go to each service → **Environment** tab and add:

### For `scientia-backend` and `scientia-celery-worker`:

| Key | Value |
|-----|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `CLOUDINARY_CLOUD_NAME` | From cloudinary.com dashboard |
| `CLOUDINARY_API_KEY` | From cloudinary.com dashboard |
| `CLOUDINARY_API_SECRET` | From cloudinary.com dashboard |
| `GOOGLE_CLIENT_ID` | From Google Cloud Console (optional) |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console (optional) |
| `GOOGLE_REDIRECT_URI` | `https://scientia-frontend.onrender.com/auth/google/callback` |

### For `scientia-frontend`:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://scientia-backend.onrender.com/api/v1` |

---

## Step 4 — Trigger Deployment

1. Click **Deploy** on each service, or push a commit to `main` to trigger auto-deploy
2. Wait ~5 minutes for first build (Render installs all dependencies including PyTorch)
3. Monitor logs in the Render dashboard

---

## Step 5 — Run Database Migrations

After the backend is deployed and running:

1. Go to `scientia-backend` service → **Shell** tab
2. Run:
```bash
alembic upgrade head
```

---

## Step 6 — Verify Deployment

- Backend health: `https://scientia-backend.onrender.com/health`
- API docs: `https://scientia-backend.onrender.com/docs`
- Frontend: `https://scientia-frontend.onrender.com`

---

## Setting Up GitHub Actions Auto-Deploy

1. In the Render dashboard, go to `scientia-backend` → **Settings** → copy the **Deploy Hook URL**
2. In GitHub repo → **Settings** → **Secrets** → add:
   - `RENDER_DEPLOY_HOOK` = the URL you copied
   - `ANTHROPIC_API_KEY` = your key (for tests)
3. Now every push to `main` runs tests then triggers a Render deploy

---

## Important Notes for Free Tier

- Free Render services **spin down** after 15 minutes of inactivity — first request after spin-down takes ~30 seconds
- PostgreSQL free tier has a **90-day limit** — upgrade to paid for production
- Celery worker on free tier may have memory limits — monitor logs for OOM errors
- FAISS index is stored in-memory — it resets on service restart. For persistence, store embeddings in the database and rebuild on startup

---

## Upgrading to Production

When ready for real traffic:
- Upgrade PostgreSQL to **Starter** ($7/month)
- Upgrade backend to **Starter** ($7/month) for always-on
- Consider adding a persistent disk for FAISS indexes
- Enable Render's auto-scaling for the backend
