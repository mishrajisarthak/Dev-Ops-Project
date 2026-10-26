from datetime import UTC, datetime
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, or_, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import get_db
from .models import Book, Loan, Member
from .schemas import BookCreate, BookResponse, LoanCreate, LoanResponse, MemberCreate, MemberResponse, MemberUpdate

app = FastAPI(title="Folio Library API", description="Catalog, members and circulation for the Folio library workspace.", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


def required(db: Session, model, record_id: int):
    record = db.get(model, record_id)
    if record is None:
        raise HTTPException(404, f"{model.__name__} not found")
    return record


def commit(db: Session):
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "ISBN or email already exists, or this record is referenced by a loan") from exc


@app.get("/")
def root():
    return {"service": "Folio Library API", "status": "UP", "docs_url": "/docs", "health_url": "/health", "metrics_url": "/metrics"}


@app.get("/health", tags=["Probes"])
def health_check():
    return {"status": "UP", "version": "2.0.0"}


@app.get("/ready", tags=["Probes"])
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "READY"}
    except Exception as exc:
        raise HTTPException(503, "Database connectivity check failed") from exc


@app.get("/api/books", response_model=list[BookResponse], tags=["Catalog"])
def list_books(q: str = "", category: str = "", availability: Literal["", "available", "borrowed"] = "", db: Session = Depends(get_db)):
    stmt = select(Book)
    if q.strip():
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(or_(Book.title.ilike(pattern), Book.author.ilike(pattern), Book.isbn.ilike(pattern)))
    if category:
        stmt = stmt.where(Book.category == category)
    if availability == "available":
        stmt = stmt.where(Book.available_copies > 0)
    elif availability == "borrowed":
        stmt = stmt.where(Book.available_copies < Book.total_copies)
    return list(db.scalars(stmt.order_by(Book.id)).all())


@app.post("/api/books", response_model=BookResponse, status_code=201, tags=["Catalog"])
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    book = Book(**payload.model_dump(), available_copies=payload.total_copies)
    db.add(book)
    commit(db)
    db.refresh(book)
    return book


@app.get("/api/books/{book_id}", response_model=BookResponse, tags=["Catalog"])
def get_book(book_id: int, db: Session = Depends(get_db)):
    return required(db, Book, book_id)


@app.put("/api/books/{book_id}", response_model=BookResponse, tags=["Catalog"])
def update_book(book_id: int, payload: BookCreate, db: Session = Depends(get_db)):
    book = db.scalar(select(Book).where(Book.id == book_id).with_for_update())
    if book is None:
        raise HTTPException(404, "Book not found")
    borrowed = book.total_copies - book.available_copies
    if payload.total_copies < borrowed:
        raise HTTPException(409, "Total copies cannot be less than copies currently on loan")
    for key, value in payload.model_dump().items():
        setattr(book, key, value)
    book.available_copies = payload.total_copies - borrowed
    commit(db)
    db.refresh(book)
    return book


@app.delete("/api/books/{book_id}", status_code=204, tags=["Catalog"])
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = required(db, Book, book_id)
    if db.scalar(select(func.count()).select_from(Loan).where(Loan.book_id == book_id)):
        raise HTTPException(409, "Books with loan history must be retained")
    db.delete(book)
    commit(db)


@app.get("/api/members", response_model=list[MemberResponse], tags=["Members"])
def list_members(q: str = "", db: Session = Depends(get_db)):
    stmt = select(Member)
    if q.strip():
        stmt = stmt.where(or_(Member.name.ilike(f"%{q.strip()}%"), Member.email.ilike(f"%{q.strip()}%")))
    return list(db.scalars(stmt.order_by(Member.id)).all())


@app.post("/api/members", response_model=MemberResponse, status_code=201, tags=["Members"])
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    member = Member(**payload.model_dump())
    db.add(member)
    commit(db)
    db.refresh(member)
    return member


@app.put("/api/members/{member_id}", response_model=MemberResponse, tags=["Members"])
def update_member(member_id: int, payload: MemberUpdate, db: Session = Depends(get_db)):
    member = required(db, Member, member_id)
    for key, value in payload.model_dump().items():
        setattr(member, key, value)
    commit(db)
    db.refresh(member)
    return member


@app.get("/api/loans", response_model=list[LoanResponse], tags=["Circulation"])
def list_loans(status: Literal["all", "active", "overdue", "returned"] = "all", db: Session = Depends(get_db)):
    stmt = select(Loan)
    if status in ("active", "overdue"):
        stmt = stmt.where(Loan.returned_at.is_(None))
    if status == "overdue":
        stmt = stmt.where(Loan.due_date < datetime.now(UTC).date())
    if status == "returned":
        stmt = stmt.where(Loan.returned_at.is_not(None))
    return list(db.scalars(stmt.order_by(Loan.id.desc())).all())


@app.post("/api/loans", response_model=LoanResponse, status_code=201, tags=["Circulation"])
def issue_loan(payload: LoanCreate, db: Session = Depends(get_db)):
    required(db, Book, payload.book_id)
    member = required(db, Member, payload.member_id)
    if not member.active:
        raise HTTPException(409, "This member is inactive")
    changed = db.execute(update(Book).where(Book.id == payload.book_id, Book.available_copies > 0).values(available_copies=Book.available_copies - 1))
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "No copies available for this book")
    loan = Loan(**payload.model_dump())
    db.add(loan)
    commit(db)
    db.refresh(loan)
    return loan


@app.post("/api/loans/{loan_id}/return", response_model=LoanResponse, tags=["Circulation"])
def return_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = required(db, Loan, loan_id)
    changed = db.execute(update(Loan).where(Loan.id == loan_id, Loan.returned_at.is_(None)).values(returned_at=datetime.now(UTC)))
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "This loan has already been returned")
    db.execute(update(Book).where(Book.id == loan.book_id).values(available_copies=Book.available_copies + 1))
    commit(db)
    db.refresh(loan)
    return loan


@app.get("/api/stats", tags=["Reports"])
def stats(db: Session = Depends(get_db)):
    today = datetime.now(UTC).date()

    def count(model, *conditions):
        return db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0

    return {
        "total_titles": count(Book),
        "total_copies": db.scalar(select(func.coalesce(func.sum(Book.total_copies), 0))),
        "available_copies": db.scalar(select(func.coalesce(func.sum(Book.available_copies), 0))),
        "active_members": count(Member, Member.active.is_(True)),
        "active_loans": count(Loan, Loan.returned_at.is_(None)),
        "overdue_loans": count(Loan, Loan.returned_at.is_(None), Loan.due_date < today),
        "returned_loans": count(Loan, Loan.returned_at.is_not(None)),
        "categories": [
            {"name": name, "count": total} for name, total in db.execute(select(Book.category, func.count()).group_by(Book.category).order_by(Book.category))
        ],
    }
