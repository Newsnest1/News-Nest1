# News Aggregator

A minimal, layered **FastAPI + PostgreSQL + MeiliSearch** news‑aggregation service.

## Quick start (Docker)

```bash
git clone <your-fork-url> news-aggregator
cd news-aggregator
cp .env.example .env               # put your NEWSAPI_KEY here
docker compose up --build
```

The API is then available at `http://localhost:8000/v1/feed`.

### Endpoints

| Method | Path          | Description         |
|--------|-------------- |---------------------|
| GET    | /v1/feed      | Latest aggregated articles |
| GET    | /v1/search    | Full‑text search (stub)   |

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Architecture

See `docs/diagram.md` and comments in source code for a full breakdown.

## License

MIT
