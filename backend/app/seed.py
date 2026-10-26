"""Explicit, repeatable demo seed. Never runs automatically in production."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from .db import SessionLocal
from .models import Book, Loan, Member

BOOKS = [
    (
        "The Midnight Library",
        "Matt Haig",
        "9780525559474",
        "Fiction",
        "A-01",
        4,
        "Between life and death there is a library, and within that library, the shelves go on forever.",
    ),
    (
        "Atomic Habits",
        "James Clear",
        "9780735211292",
        "Personal growth",
        "B-03",
        3,
        "Small changes, remarkable results. A practical guide to building better habits.",
    ),
    ("The Creative Act", "Rick Rubin", "9780593652886", "Design", "C-02", 2, "A generous invitation to discover creativity as a way of being."),
    ("The Psychology of Money", "Morgan Housel", "9780857197689", "Personal growth", "B-04", 3, "Timeless lessons on wealth, greed, and happiness."),
    ("A Brief History of Time", "Stephen Hawking", "9780553380163", "Science", "D-01", 2, "A journey through space, time, and the mysteries of our universe."),
    ("Clean Code", "Robert C. Martin", "9780132350884", "Technology", "E-02", 3, "A handbook of agile software craftsmanship and thoughtful engineering."),
    ("Sapiens", "Yuval Noah Harari", "9780062316097", "History", "F-01", 2, "A brief history of humankind, from the Stone Age to the present."),
    ("The Design of Everyday Things", "Don Norman", "9780465050659", "Design", "C-01", 2, "Discover the thoughtful design behind the things we use every day."),
]
MEMBERS = [
    ("Maya Patel", "maya.patel@example.com"),
    ("Arjun Mehta", "arjun.mehta@example.com"),
    ("Sofia Chen", "sofia.chen@example.com"),
    ("Oliver James", "oliver.james@example.com"),
    ("Aisha Khan", "aisha.khan@example.com"),
    ("Noah Williams", "noah.williams@example.com"),
]


def seed():
    with SessionLocal() as db:
        if db.scalar(select(Book.id).limit(1)) or db.scalar(select(Member.id).limit(1)):
            print("Library already contains records; seed skipped (no changes).")
            return
        now = datetime.now(UTC)
        books = []
        for title, author, isbn, category, shelf, copies, description in BOOKS:
            book = Book(
                title=title, author=author, isbn=isbn, category=category, shelf=shelf, total_copies=copies, available_copies=copies, description=description
            )
            db.add(book)
            books.append(book)
        members = [Member(name=name, email=email, joined_at=now - timedelta(days=20 + i * 4)) for i, (name, email) in enumerate(MEMBERS)]
        db.add_all(members)
        db.flush()
        for index, days in [(0, 8), (1, 5), (4, -2), (5, 10), (6, -1)]:
            books[index].available_copies -= 1
            db.add(
                Loan(
                    book_id=books[index].id,
                    member_id=members[index % len(members)].id,
                    borrowed_at=now - timedelta(days=14 - days),
                    due_date=now.date() + timedelta(days=days),
                )
            )
        db.add(
            Loan(
                book_id=books[2].id,
                member_id=members[2].id,
                borrowed_at=now - timedelta(days=5),
                due_date=now.date() + timedelta(days=9),
                returned_at=now - timedelta(days=1),
            )
        )
        db.commit()
        print("Seeded 8 titles, 21 copies, 6 members, 5 open loans (2 overdue), and 1 returned loan.")


if __name__ == "__main__":
    seed()
