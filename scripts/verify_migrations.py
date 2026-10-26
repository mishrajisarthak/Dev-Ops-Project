"""Verify new installs, additive legacy upgrades, and a reversible library migration."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from sqlalchemy import create_engine, inspect, text

BACKEND = Path(__file__).resolve().parents[1] / "backend"


def main():
    with tempfile.TemporaryDirectory(prefix="folio-migrations-") as temporary:
        database = Path(temporary) / "migration.db"
        env = {**os.environ, "DATABASE_URL": f"sqlite:///{database.as_posix()}"}
        run = lambda *args: subprocess.run([sys.executable, "-m", "alembic", *args], cwd=BACKEND, env=env, check=True)
        run("upgrade", "0001_initial_items")
        engine = create_engine(env["DATABASE_URL"])
        with engine.begin() as connection:
            connection.execute(text("INSERT INTO items (title, category, description, found_by, finder_contact, location_found, collection_point, status, found_at, created_at) VALUES ('Legacy fixture', 'Test', '', 'Tester', 'test@example.com', 'Campus', 'Reception Desk', 'found', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"))
        run("upgrade", "head")
        assert {"books", "members", "loans", "items"} <= set(inspect(engine).get_table_names())
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT title FROM items")) == "Legacy fixture"
        print("PASS additive library upgrade preserves legacy records")
        run("downgrade", "0001_initial_items")
        assert "books" not in inspect(engine).get_table_names()
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT COUNT(*) FROM items")) == 1
        run("upgrade", "head")
        print("PASS downgrade and re-upgrade retain legacy data and recreate library schema")
        engine.dispose()


if __name__ == "__main__":
    main()
