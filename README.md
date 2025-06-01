# News Nest v0.1 – Docker-First News Aggregator

> **Tagline:** Real-time headlines & lightning-fast search, fully containerised with FastAPI + PostgreSQL + MeiliSearch.

---

## 🎯  What’s in this release

| 🚀 Feature | Details |
|-----------|---------|
| **🐳 Full Docker Compose** | Single-command launch for prod & dev |
| **⚡ Live Feed Aggregation** | Pulls NewsAPI + unlimited RSS feeds |
| **🔎 Instant Search (MeiliSearch)** | Keyword & "More-like-this" vector search (stub for now) |
| **📊 Postgres Persistence** | Durable article store with migrations |
| **🩺 Health Checks** | `/livez`, `/readyz`, and container health definitions |
| **🔒 Hardened Containers** | Non-root images, read-only FS, env-only secrets |
| **📑 Hexagonal Architecture** | Presentation → Service → Business → Persistence → Adapters |
| **🧪 CI Pipeline** | Ruff, pytest, and Docker build on every push |

---

## 📋  Table of Contents
1. [Quick Start (Docker)](#quick-start-docker)
2. [Project Overview](#project-overview)
3. [Docker Deployment](#docker-deployment)
4. [Development Setup](#development-setup)
5. [Architecture & Features](#architecture--features)
6. [Testing](#testing)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)
9. [Roadmap](#roadmap)
10. [License & Contributing](#license--contributing)

---

## 🚀  Quick Start (Docker)
Launch News Nest in **< 3 min**:

### Prerequisites
* Docker Desktop (macOS/Windows) *or* Docker Engine 20.10+ (Linux)
* Docker Compose plugin (bundled with Docker Desktop)
* Git

### 1 · Clone the repo
```bash
git clone https://github.com/<you>/news-nest.git
cd news-nest
```

### 2 · Create `.env`
```bash
cp .env.example .env            # edit and paste your NEWSAPI_KEY
```

### 3 · Start production-grade stack
```bash
docker compose up --build -d    # first run ≈ 2 min
```

### 4 · Hit the endpoints
| URL | Purpose |
|------|---------|
| http://localhost:8000/v1/feed | Latest aggregated articles |
| http://localhost:8000/v1/search?q=ai | Search (stub) |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/readyz | Readiness probe |

That’s it!  All services are up and networked.

---

## 📖  Project Overview
**News Nest** ingests public news sources, de-duplicates, enriches, and serves them through a clean API (and optional React front-end).

### Tech Stack
* **Backend:** Python 3.11, FastAPI, Uvicorn
* **Database:** PostgreSQL 16 (with Alembic migrations)
* **Search:** MeiliSearch 1.4 (vector-ready)
* **Queue / Async:** Native `asyncio` (Celery optional later)
* **Containerisation:** Docker & Docker Compose
* **CI/CD:** GitHub Actions, Docker Hub (optional)

---

## 🐳  Docker Deployment

### Architecture (production compose)
```
┌───────────────┐    ┌────────────────┐    ┌────────────────┐
│   Nginx *     │    │  FastAPI App   │    │  MeiliSearch   │
│  (optional)   │──▶ │ (Uvicorn, 8000)│──▶ │  Port 7700     │
└───────────────┘    └────────────────┘    └────────────────┘
          │                    │                    │
          └────────────────────┴────────────────────┘
                               │
                         ┌──────────────┐
                         │  Postgres    │
                         │  Port 5432   │
                         └──────────────┘
```
*Nginx is commented out by default; enable for SSL & rate-limiting.*

### Available Compose files
| File | Purpose |
|------|---------|
| `docker-compose.yml` | Production-like stack (FastAPI, Postgres, MeiliSearch) |
| `docker-compose.dev.yml` | Dev overrides with code bind-mount & auto-reload |

### Common Make targets
```bash
make build   # docker compose build
make up      # docker compose up -d (prod)
make dev-up  # docker compose -f ...dev.yml up
make logs    # tail all service logs
make test    # run pytest inside container
```

---

## 🛠️  Development Setup

### Option 1 – Docker Dev (recommended)
```bash
make dev-up         # starts api + db + search with live reload
make dev-logs       # follow logs
make dev-down       # stop
```

### Option 2 – Local venv
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export NEWSAPI_KEY=xxx
uvicorn app.main:app --reload
```
*(requires Postgres & MeiliSearch running locally)*

---

## 🏗️  Architecture & Features

### Hexagonal Layer Diagram
```
... (diagram truncated for brevity in example) ...
```
*(diagram shows Presentation → Service → Business → Persistence → Adapters → DB)*

### Core Features
* **Aggregation:** pulls from unlimited RSS/NewsAPI sources; de-dupes via SHA-256(title+source).
* **Enrichment (stub):** ready for language-detect, summary, embeddings.
* **Search:** MeiliSearch full-text, filters (`topic`, `source`, `date`).
* **Personalisation (roadmap):** per-user prefs, pgvector similarity.

---

## 🧪  Testing

| Kind | Tool | Where |
|------|------|-------|
| Unit & Integration | **pytest** | `tests/` |
| Lint & Formatting | **ruff**, **black** | CI & pre-commit |
| CI Pipeline | GitHub Actions | `.github/workflows/ci.yml` |

Run locally:
```bash
make test          # via Docker
# OR
pytest -q          # inside venv
```

---

## ⚙️  Configuration
All options are env-vars (see `.env.example`).

```env
# Required
NEWSAPI_KEY=your-newsapi-key

# Optional
DATABASE_URL=postgresql+psycopg2://news:news@db:5432/news
MEILI_HOST=http://search:7700
MEILI_MASTER_KEY=masterKey
FEED_SOURCES=rss:https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml,rss:https://feeds.bbci.co.uk/news/world/rss.xml
```

Customise per-env with `docker-compose.override.yml` or a secrets manager.

---

## 🩹  Troubleshooting
| Symptom | Cause | Fix |
|---------|-------|-----|
| `bind: address already in use :5432` | Host Postgres already running | Edit compose: `15432:5432` or stop local Postgres |
| Feed returns `[]` | NewsAPI rate-limited | Add more RSS feeds; increase `limit` param |
| `/search` 500 error | MeiliSearch not up | `docker compose logs search`, ensure port 7700 free |
| `KeyError: NEWSAPI_KEY` | `.env` missing key | Edit `.env`, `docker compose restart api` |

---

## 🗺️  Roadmap
* Vector similarity search (pgvector)
* Automatic article summaries (OpenAI GPT-4o)
* Auth & user feed personalisation
* Nginx reverse proxy with rate-limit + SSL
* Kubernetes Helm chart

---

## 📄  License & Contributing
MIT License. Feel free to fork & PR!

1. Fork ➜ Branch ➜ Commit w/ tests ➜ PR to `main`.
2. Ensure `make test` & `ruff` pass locally.

