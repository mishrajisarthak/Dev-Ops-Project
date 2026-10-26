from datetime import UTC, date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]


class BookCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=2, max_length=160)
    author: Name
    isbn: str = Field(pattern=r"^(?:[0-9]{10}|[0-9]{13})$")
    category: str = Field(min_length=2, max_length=60)
    shelf: str = Field(default="A-01", min_length=1, max_length=30)
    description: str = Field(default="", max_length=1000)
    total_copies: int = Field(default=1, ge=1, le=1000)


class BookResponse(BookCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    available_copies: int
    created_at: datetime


class MemberCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: Name
    email: str = Field(min_length=5, max_length=180, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class MemberResponse(MemberCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    active: bool
    joined_at: datetime


class MemberUpdate(MemberCreate):
    active: bool = True


class LoanCreate(BaseModel):
    book_id: int = Field(gt=0)
    member_id: int = Field(gt=0)
    due_date: date

    @field_validator("due_date")
    @classmethod
    def future_due_date(cls, value: date) -> date:
        if value < datetime.now(UTC).date():
            raise ValueError("Due date cannot be in the past")
        return value


class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    book_id: int
    member_id: int
    book_title: str
    member_name: str
    borrowed_at: datetime
    due_date: date
    returned_at: datetime | None
    status: str
