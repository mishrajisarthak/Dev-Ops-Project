from datetime import UTC, date, datetime

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint("total_copies > 0", name="ck_book_total"),
        CheckConstraint("available_copies >= 0 AND available_copies <= total_copies", name="ck_book_available"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    author: Mapped[str] = mapped_column(String(120))
    isbn: Mapped[str] = mapped_column(String(13), unique=True)
    category: Mapped[str] = mapped_column(String(60), index=True)
    shelf: Mapped[str] = mapped_column(String(30), default="A-01")
    description: Mapped[str] = mapped_column(String(1000), default="")
    total_copies: Mapped[int] = mapped_column(default=1)
    available_copies: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class Member(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(180), unique=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class Loan(Base):
    __tablename__ = "loans"
    __table_args__ = (Index("ix_loans_active_due", "returned_at", "due_date"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    borrowed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    due_date: Mapped[date] = mapped_column(Date)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    book: Mapped[Book] = relationship(lazy="joined")
    member: Mapped[Member] = relationship(lazy="joined")

    @property
    def book_title(self) -> str:
        return self.book.title

    @property
    def member_name(self) -> str:
        return self.member.name

    @property
    def status(self) -> str:
        if self.returned_at:
            return "returned"
        return "overdue" if self.due_date < datetime.now(UTC).date() else "active"
