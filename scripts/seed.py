"""Seed the configured database; run migrations first. Uses DATABASE_URL when set."""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.exit(
        subprocess.call(
            [sys.executable, "-m", "app.seed"],
            cwd=Path(__file__).resolve().parents[1] / "backend",
        )
    )
