# News Nest – FastAPI‑based News Aggregator

News Nest collects articles from public sources in near real‑time, stores them in PostgreSQL, and serves them through a clean REST API.  



---

## Contents

1. [Quick start](#quick-start)
2. [System overview](#system-overview)
3. [Running with Docker](#running-with-docker)
4. [Development workflow](#development-workflow)
5. [Architecture](#architecture)
6. [Testing and quality](#testing-and-quality)


---

## Quick start

```bash
git clone https://github.com/Newsnest1/news-nest1.git
cd news-nest1
cp .env.example .env
nano .env
nano docker-compose.yml
Port 15432:5432
"8000:8000"
docker compose up --build -d
curl http://localhost:8000/v1/feed | head
```

Available endpoints once the containers are up:

| Path | Purpose |
|------|---------|
| `/v1/feed` | latest articles |
| `/v1/search` | search (stub) |
| `/docs` | Swagger UI |
| `/readyz` | readiness check |


---

## System overview

* **Language:** Python 3.11  
* **Framework:** FastAPI with Uvicorn ASGI server  
* **Database:** PostgreSQL 16  
* **Search engine:** MeiliSearch 1.4  
* **Containerisation:** Docker & Docker Compose  
* **Continuous integration:** GitHub Actions (lint, tests, image build)

---

## Running with Docker

The default `docker-compose.yml` starts three containers:

```
fastapi  (port 8000)  ─┐
postgres (port 5432)  ─┼─ internal Docker network
meilisearch (7700)   ─┘
```

There is also a `docker-compose.dev.yml` overlay that mounts the source tree
and runs Uvicorn in reload mode for rapid iteration.

Common commands:

```bash
make build        # docker compose build
make up           # start production‑style stack
make down         # stop containers
make dev-up       # start dev stack with code hot‑reload
make logs         # tail all service logs
make test         # run pytest in container
```

---

## Development workflow

Docker dev stack 

```bash
make dev-up
make dev-logs     
make dev-down

```

You will still need Postgres and MeiliSearch running locally or in Docker.

---

## Architecture

The project follows a hexagonal design separated into six layers.

```
┌────────────────────────────────────────────────────────────┐
│                Presentation Layer                          │
│  ┌────────────┐ ┌───────────────┐ ┌──────────────┐        │
│  │ Web routes │ │   API routes  │ │   Templates  │        │
│  └────────────┘ └───────────────┘ └──────────────┘        │
└────────────────────────────────────────────────────────────┘
                               │
┌────────────────────────────────────────────────────────────┐
│                  Service Layer                             │
│  Feed service • Search service • User service              │
└────────────────────────────────────────────────────────────┘
                               │
┌────────────────────────────────────────────────────────────┐
│                  Business Layer                            │
│  Aggregation logic • Personalisation engine • Entities     │
└────────────────────────────────────────────────────────────┘
                               │
┌────────────────────────────────────────────────────────────┐
│                 Persistence Layer                          │
│  SQLAlchemy models • Repositories • Object mappers         │
└────────────────────────────────────────────────────────────┘
                               │
┌────────────────────────────────────────────────────────────┐
│                  Adapters Layer                            │
│  NewsAPI client • RSS client • MeiliSearch client          │
└────────────────────────────────────────────────────────────┘
                               │
┌────────────────────────────────────────────────────────────┐
│                   Database Layer                           │
│  PostgreSQL • MeiliSearch index • Optional blob store      │
└────────────────────────────────────────────────────────────┘
```

---

## Testing and quality

* **Unit & integration tests:** `pytest` in `tests/`
* **Static checks:** `ruff` (lint) and `black` (format)
* **CI:** GitHub Actions workflow in `.github/workflows/ci.yml`

Run everything locally:

```bash
pytest -q
ruff app
```


