import os
import sys
from pathlib import Path
from alembic.config import Config
from alembic import command


def run_migrations():
    backend_dir = Path(__file__).resolve().parent.parent
    if not (backend_dir / "alembic.ini").exists():
        backend_dir = Path(sys.prefix) / "share" / "folio"
    alembic_ini_path = backend_dir / "alembic.ini"
    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))

    db_url = os.getenv("DATABASE_URL")
    if db_url:
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    print("Running database migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Database migrations applied successfully.")


if __name__ == "__main__":
    try:
        run_migrations()
    except Exception as e:
        print(f"Migration error: {e}", file=sys.stderr)
        sys.exit(1)
