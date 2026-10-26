"""Exercise a running API, including write, checkout, return, and stock restoration."""

import json
import sys
import urllib.request
from datetime import UTC, datetime, timedelta
from uuid import uuid4

base = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")


def call(path, method="GET", body=None):
    request = urllib.request.Request(
        base + path,
        method=method,
        data=json.dumps(body).encode() if body else None,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        data = response.read()
        print(f"PASS {method:6} {path} -> {response.status}")
        return json.loads(data) if data else None


def main():
    assert call("/health")["status"] == "UP"
    assert call("/ready")["status"] == "READY"
    for path in ("/api/books", "/api/members", "/api/loans", "/api/stats"):
        call(path)
    token = uuid4().hex[:10]
    # Smoke records are retained as circulation history, clearly named for identification.
    book = call(
        "/api/books",
        "POST",
        {
            "title": "Smoke Test Handbook",
            "author": "Folio QA",
            "isbn": str(int(uuid4().hex[:10], 16)).zfill(13),
            "category": "Technology",
            "total_copies": 1,
        },
    )
    member = call(
        "/api/members",
        "POST",
        {"name": "Smoke Test Reader", "email": f"smoke-{token}@example.com"},
    )
    loan = call(
        "/api/loans",
        "POST",
        {
            "book_id": book["id"],
            "member_id": member["id"],
            "due_date": (datetime.now(UTC).date() + timedelta(days=14)).isoformat(),
        },
    )
    assert call(f"/api/books/{book['id']}")["available_copies"] == 0
    assert call(f"/api/loans/{loan['id']}/return", "POST")["status"] == "returned"
    assert call(f"/api/books/{book['id']}")["available_copies"] == 1
    print(
        "PASS full library lifecycle; inventory restored. Test loan retained for audit."
    )


if __name__ == "__main__":
    main()
