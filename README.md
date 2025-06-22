# News-Nest1

News-Nest collects articles from public sources in near real-time, stores them in PostgreSQL, and serves them through a clean REST API.  



---

## Contents

1. [Quick start](#quick-start)
2. [System overview](#system-overview)
3. [Running with Docker](#running-with-docker)
4. [Development workflow](#development-workflow)
5. [Architecture](#architecture)
6. [Testing and quality](#testing-and-quality)
7. [User Features](#user-features)
8. [API Response Fields](#api-response-fields)


---

## Quick start

```bash
git clone https://github.com/Newsnest1/News-Nest1.git
cd News-Nest1
# Create a .env file with your settings (see below for required variables)
nano .env
docker compose up --build -d
# Wait for containers to be healthy, then:
curl http://localhost:8001/v1/feed | head
```

**Default exposed ports:**
- FastAPI: `8001`
- Postgres: `5433`
- MeiliSearch: `7701`

**Endpoints:**
| Path | Purpose |
|------|---------|
| `/v1/feed` | latest articles |
| `/v1/search` | search |
| `/docs` | Swagger UI |
| `/readyz` | readiness check |

**Note:**  
If you need to configure environment variables, create a `.env` file in the project root.  
Example variables:
```
POSTGRES_USER=news
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=news
MEILI_MASTER_KEY=yourmeilikey
```


---

## System overview

* **Language:** Python 3.11  
* **Framework:** FastAPI with Uvicorn ASGI server  
* **Database:** PostgreSQL 16  
* **Search engine:** MeiliSearch 1.4  
* **Containerisation:** Docker & Docker Compose  
* **Continuous integration:** GitHub Actions (lint, tests, image build)

---

## Running with Docker

The default `docker-compose.yml` starts three containers:

```
fastapi  (port 8001)  ─┐
postgres (port 5433)  ─┼─ internal Docker network
meilisearch (7701)   ─┘
```

Common commands:

```bash
docker compose build        # Build the images
docker compose up -d        # Start the stack in detached mode
docker compose down         # Stop containers
docker compose logs         # Tail all service logs
```

---

## Development workflow

- Use the Docker Compose stack for local development.
- Edit your code and restart the relevant service if needed.
- You will still need Postgres and MeiliSearch running locally or in Docker.

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


---

## User Features

### Save Articles
- **Save an article:**
  - `POST /v1/users/me/saved?article_url=...`
- **Remove a saved article:**
  - `DELETE /v1/users/me/saved?article_url=...`
- **List saved articles:**
  - `GET /v1/users/me/saved`

### Personalized Feed
- **Get personalized feed:**
  - `GET /v1/feed/personalized`
  - Returns articles from your followed topics and outlets, with an `is_saved` field for each article.

### Follow Topics and Outlets
- **Follow a topic:**
  - `POST /v1/users/me/follow/topic?topic=...`
- **Unfollow a topic:**
  - `DELETE /v1/users/me/follow/topic?topic=...`
- **List followed topics:**
  - `GET /v1/users/me/followed/topics`
- **Follow an outlet:**
  - `POST /v1/users/me/follow/outlet?outlet=...`
- **Unfollow an outlet:**
  - `DELETE /v1/users/me/follow/outlet?outlet=...`
- **List followed outlets:**
  - `GET /v1/users/me/followed/outlets`


---

## API Response Fields
- `is_saved`: `true` if you have saved the article, `false` otherwise.


