"""Live HTTP race tests: one copy cannot be checked out or returned twice."""

import json
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from uuid import uuid4

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"


def call(path, method="GET", payload=None):
    request = urllib.request.Request(
        BASE + path,
        method=method,
        data=json.dumps(payload).encode() if payload else None,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())


def main():
    token = uuid4().hex[:8]
    status, book = call(
        "/api/books",
        "POST",
        {
            "title": f"Concurrency Test {token}",
            "author": "Folio QA",
            "isbn": str(int(uuid4().hex[:10], 16)).zfill(13),
            "category": "Technology",
            "total_copies": 1,
        },
    )
    assert status == 201
    status, member = call(
        "/api/members",
        "POST",
        {"name": "Concurrent Reader", "email": f"race-{token}@example.com"},
    )
    assert status == 201
    payload = {
        "book_id": book["id"],
        "member_id": member["id"],
        "due_date": (datetime.now(UTC).date() + timedelta(days=14)).isoformat(),
    }
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(
            pool.map(lambda _: call("/api/loans", "POST", payload), range(8))
        )
    codes = [code for code, _ in results]
    assert codes.count(201) == 1 and codes.count(409) == 7, codes
    assert call(f"/api/books/{book['id']}")[1]["available_copies"] == 0
    print("PASS 8 simultaneous checkouts: 1 issued, 7 conflicts, stock = 0")
    loan = next(body for code, body in results if code == 201)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(
            pool.map(
                lambda _: call(f"/api/loans/{loan['id']}/return", "POST"), range(8)
            )
        )
    codes = [code for code, _ in results]
    assert codes.count(200) == 1 and codes.count(409) == 7, codes
    assert call(f"/api/books/{book['id']}")[1]["available_copies"] == 1
    print("PASS 8 simultaneous returns: 1 returned, 7 conflicts, stock = 1")


if __name__ == "__main__":
    main()
