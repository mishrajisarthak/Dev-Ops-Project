"""Compare full library records across PostgreSQL + backend container restarts."""

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"


def fetch(path):
    with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=10) as response:
        return json.loads(response.read())


def snapshot():
    return {
        kind: sorted(fetch(f"/api/{kind}"), key=lambda record: record["id"])
        for kind in ("books", "members", "loans")
    }


def main():
    before = snapshot()
    if not before["books"]:
        raise RuntimeError("Seed the database before testing persistence")
    print("Before restart:", {key: len(records) for key, records in before.items()})
    subprocess.run(["docker", "compose", "restart", "postgres", "backend"], check=True)
    for attempt in range(60):
        try:
            if fetch("/ready")["status"] == "READY":
                break
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
            if attempt == 59:
                raise
            time.sleep(1)
    after = snapshot()
    assert before == after, "Persisted library records changed after restart"
    print("After restart:", {key: len(records) for key, records in after.items()})
    print(
        "PASS: all book, member and loan fields retained across database and application restarts."
    )


if __name__ == "__main__":
    main()
