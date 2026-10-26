from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.models import Book, Loan

BOOK = {"title": "The Midnight Library", "author": "Matt Haig", "isbn": "9780525559474", "category": "Fiction", "shelf": "A-01", "total_copies": 2}
MEMBER = {"name": "Maya Patel", "email": "maya@example.com"}


def setup_loan(client, copies=2):
    book = client.post("/api/books", json={**BOOK, "total_copies": copies}).json()
    member = client.post("/api/members", json=MEMBER).json()
    payload = {"book_id": book["id"], "member_id": member["id"], "due_date": (datetime.now(UTC).date() + timedelta(days=14)).isoformat()}
    return book, member, payload


def test_catalog_crud(client):
    response = client.post("/api/books", json=BOOK)
    assert response.status_code == 201
    book = response.json()
    assert book["available_copies"] == 2
    assert client.get(f"/api/books/{book['id']}").json()["title"] == BOOK["title"]
    updated = {**BOOK, "title": "A New Title", "total_copies": 4}
    assert client.put(f"/api/books/{book['id']}", json=updated).json()["available_copies"] == 4
    assert client.delete(f"/api/books/{book['id']}").status_code == 204
    assert client.get(f"/api/books/{book['id']}").status_code == 404


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", "  "),
        ("author", " "),
        ("category", " "),
        ("isbn", "123"),
        ("isbn", "978-0525559474"),
        ("total_copies", 0),
        ("total_copies", -1),
        ("total_copies", 1001),
        ("shelf", " "),
    ],
)
def test_invalid_books(client, field, value):
    assert client.post("/api/books", json={**BOOK, field: value}).status_code == 422


def test_duplicate_isbn_and_filters(client):
    client.post("/api/books", json=BOOK)
    assert client.post("/api/books", json=BOOK).status_code == 409
    for query in ("q=midnight", "q=HAIG", "q=9780525559474", "category=Fiction", "availability=available"):
        assert len(client.get(f"/api/books?{query}").json()) == 1
    assert client.get("/api/books?category=Science").json() == []
    assert client.get("/api/books?availability=borrowed").json() == []
    assert client.get("/api/books?availability=invalid").status_code == 422


def test_member_create_search_update(client):
    member = client.post("/api/members", json={**MEMBER, "email": "MAYA@EXAMPLE.COM"}).json()
    assert member["email"] == MEMBER["email"]
    assert len(client.get("/api/members?q=MAYA").json()) == 1
    assert client.post("/api/members", json=MEMBER).status_code == 409
    response = client.put(f"/api/members/{member['id']}", json={**MEMBER, "active": False})
    assert response.status_code == 200
    assert response.json()["active"] is False


@pytest.mark.parametrize("payload", [{"name": " ", "email": "x@y.com"}, {"name": "Maya", "email": "invalid"}])
def test_invalid_members(client, payload):
    assert client.post("/api/members", json=payload).status_code == 422


def test_checkout_return_and_statistics(client):
    book, member, payload = setup_loan(client)
    response = client.post("/api/loans", json=payload)
    assert response.status_code == 201
    loan = response.json()
    assert loan["status"] == "active"
    assert loan["book_title"] == BOOK["title"]
    assert loan["member_name"] == MEMBER["name"]
    assert client.get(f"/api/books/{book['id']}").json()["available_copies"] == 1
    assert len(client.get("/api/books?availability=borrowed").json()) == 1
    stats = client.get("/api/stats").json()
    assert stats["total_titles"] == 1 and stats["total_copies"] == 2
    assert stats["active_members"] == 1 and stats["active_loans"] == 1
    assert stats["categories"] == [{"name": "Fiction", "count": 1}]
    returned = client.post(f"/api/loans/{loan['id']}/return")
    assert returned.status_code == 200
    assert returned.json()["status"] == "returned"
    assert client.get(f"/api/books/{book['id']}").json()["available_copies"] == 2
    assert client.post(f"/api/loans/{loan['id']}/return").status_code == 409
    assert client.get(f"/api/books/{book['id']}").json()["available_copies"] == 2
    assert client.get("/api/stats").json()["returned_loans"] == 1
    assert client.get("/api/loans?status=active").json() == []
    assert len(client.get("/api/loans?status=returned").json()) == 1


def test_out_of_stock_does_not_oversell(client):
    book, _, payload = setup_loan(client, copies=1)
    assert client.post("/api/loans", json=payload).status_code == 201
    assert client.post("/api/loans", json=payload).status_code == 409
    assert client.get(f"/api/books/{book['id']}").json()["available_copies"] == 0
    assert len(client.get("/api/loans").json()) == 1


def test_inactive_member_cannot_borrow(client):
    book, member, payload = setup_loan(client)
    client.put(f"/api/members/{member['id']}", json={**MEMBER, "active": False})
    assert client.post("/api/loans", json=payload).status_code == 409
    assert client.get(f"/api/books/{book['id']}").json()["available_copies"] == 2


def test_past_due_checkout_rejected(client):
    _, _, payload = setup_loan(client)
    payload["due_date"] = (datetime.now(UTC).date() - timedelta(days=1)).isoformat()
    assert client.post("/api/loans", json=payload).status_code == 422


def test_overdue_and_inventory_edits(client, db_session):
    book, _, payload = setup_loan(client)
    loan = client.post("/api/loans", json=payload).json()
    db_session.get(Loan, loan["id"]).due_date = datetime.now(UTC).date() - timedelta(days=1)
    db_session.commit()
    assert client.get("/api/loans?status=overdue").json()[0]["status"] == "overdue"
    assert client.get("/api/stats").json()["overdue_loans"] == 1
    assert client.put(f"/api/books/{book['id']}", json={**BOOK, "total_copies": 3}).json()["available_copies"] == 2
    client.post("/api/loans", json=payload)
    assert client.put(f"/api/books/{book['id']}", json={**BOOK, "total_copies": 1}).status_code == 409
    assert client.delete(f"/api/books/{book['id']}").status_code == 409
    assert db_session.scalar(select(Book.available_copies)) == 1


def test_history_retained_after_return(client):
    book, _, payload = setup_loan(client)
    loan = client.post("/api/loans", json=payload).json()
    client.post(f"/api/loans/{loan['id']}/return")
    assert client.delete(f"/api/books/{book['id']}").status_code == 409


@pytest.mark.parametrize(
    "method,url,payload",
    [
        ("get", "/api/books/999", None),
        ("delete", "/api/books/999", None),
        ("put", "/api/books/999", BOOK),
        ("put", "/api/members/999", {**MEMBER, "active": True}),
        ("post", "/api/loans/999/return", None),
    ],
)
def test_not_found(client, method, url, payload):
    assert getattr(client, method)(url, **({"json": payload} if payload else {})).status_code == 404


def test_missing_checkout_references(client):
    payload = {"book_id": 999, "member_id": 999, "due_date": datetime.now(UTC).date().isoformat()}
    assert client.post("/api/loans", json=payload).status_code == 404
    book = client.post("/api/books", json=BOOK).json()
    assert client.post("/api/loans", json={**payload, "book_id": book["id"]}).status_code == 404
    assert client.get(f"/api/books/{book['id']}").json()["available_copies"] == 2


def test_empty_statistics(client):
    stats = client.get("/api/stats").json()
    assert stats["total_titles"] == stats["total_copies"] == stats["active_loans"] == 0
    assert stats["categories"] == []
