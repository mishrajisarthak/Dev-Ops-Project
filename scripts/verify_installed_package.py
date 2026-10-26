"""Run migrations, seed and API requests from the installed wheel outside the source tree."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    with tempfile.TemporaryDirectory(prefix="folio-wheel-") as temporary:
        database = Path(temporary) / "installed.db"
        env = {**os.environ, "DATABASE_URL": f"sqlite:///{database.as_posix()}"}
        for module in ("app.migrate", "app.seed", "app.seed"):
            subprocess.run([sys.executable, "-m", module], cwd=temporary, env=env, check=True)
        code = """
import app
from app.main import app as api
from fastapi.testclient import TestClient
print('Installed package:', app.__file__)
with TestClient(api) as client:
    assert client.get('/health').json()['status'] == 'UP'
    assert len(client.get('/api/books').json()) == 8
    assert client.get('/api/stats').json()['total_copies'] == 21
print('PASS installed wheel: migrations, idempotent seed, health, catalog and statistics')
"""
        subprocess.run([sys.executable, "-c", code], cwd=temporary, env=env, check=True)


if __name__ == "__main__":
    main()
