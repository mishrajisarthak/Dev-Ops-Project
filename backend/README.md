# Folio Library API

FastAPI + SQLAlchemy library catalog, membership and circulation API.
Run `python -m app.migrate` from this directory before starting
`uvicorn app.main:app --host 127.0.0.1 --port 8000`.
The default local database is SQLite; set DATABASE_URL for PostgreSQL.
See the repository README for containers, migrations, CI and testing.
