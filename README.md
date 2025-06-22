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
# Note: If the link fails, you can clone from a local path, e.g.:
# git clone /path/to/News-Nest1

cd News-Nest1
# Copy the example environment file (includes built-in MeiliSearch key)
cp .env.example .env
# Optional: Add your NewsAPI key for additional news sources
# nano .env  # Uncomment and add: NEWSAPI_KEY=your_newsapi_key_here
docker compose up --build -d
# Wait for containers to be healthy, then:
curl http://localhost:8001/v1/feed | head
```

You can also access the web interface directly in your browser at [http://localhost:8001/](http://localhost:8001/) or [http://localhost:8001/index.html](http://localhost:8001/index.html).

**Default exposed ports:**
- FastAPI: `8001`
- Postgres: `5433`
- MeiliSearch: `7701`

**Endpoints:**
| Path | Purpose |
|------|---------|
| `/v1/feed` | latest articles |
| `/v1/search` | full-text search (powered by MeiliSearch) |
| `/docs` | Swagger UI |
| `/readyz` | readiness check |

**Web Interface Features:**
- Dark/light theme toggle
- Real-time search functionality
- Responsive design
- Article categorization

**Environment Setup:**
The `.env.example` file contains all necessary configuration including the built-in MeiliSearch key. Simply copy it to `.env` and you're ready to go:

```
POSTGRES_USER=news
POSTGRES_PASSWORD=news
POSTGRES_DB=news
MEILI_MASTER_KEY=70e6fe85e4c6480082c9d9bacb26052c  # Built-in, no external key needed
# Optional: Add your NewsAPI key for additional news sources
# NEWSAPI_KEY=your_newsapi_key_here
```

**Note:** The `.env` file should be listed in your `.gitignore` and never be committed. The MeiliSearch key is built into the project and works immediately without any external API key registration.


---

## System overview

* **Language:** Python 3.11  
* **Framework:** FastAPI with Uvicorn ASGI server  
* **Database:** PostgreSQL 16  
* **Search engine:** MeiliSearch 1.4 (fully operational with full-text search)
* **Containerisation:** Docker & Docker Compose  
* **Continuous integration:** GitHub Actions (lint, tests, image build)
* **Frontend:** Static HTML/CSS/JS with responsive design and theme switching

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

- **Unit & integration tests:** `pytest` in `tests/`
- **Static checks:** `ruff` (linting)
- **CI:** GitHub Actions workflow in `.github/workflows/ci.yml`

Run checks locally:

```bash
# Lint with ruff
ruff check .

# Run tests with pytest
pytest -q
```

**Note:** The test suite requires a running PostgreSQL database. Refer to the CI workflow (`.github/workflows/ci.yml`) for an example of how to set one up.


---

## Project Requirements

### Functional Requirements (Must-Haves)

- **FR-01:** Collect articles from NewsAPI and any number of RSS feeds.
- **FR-02:** Categorise each article into Sports, Technology, Politics, Weather, Business or Other.
- **FR-03:** Full-text search of headline and summary.
- **FR-04:** Filter feed by category parameter.
- **FR-05:** WebSocket push – notify clients when the feed is refreshed.

### Nice-to-Have Features

- Favorize articles.
- Provide a function to follow news outlets, reporters, or categories.
- Push Notifications.
- Allow users to create an account.

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
