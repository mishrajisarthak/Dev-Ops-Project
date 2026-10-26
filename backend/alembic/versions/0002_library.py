"""Add library tables; retain any existing legacy items without destructive conversion."""
import sqlalchemy as sa
from alembic import op

revision = "0002_library"
down_revision = "0001_initial_items"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("author", sa.String(120), nullable=False),
        sa.Column("isbn", sa.String(13), nullable=False, unique=True),
        sa.Column("category", sa.String(60), nullable=False),
        sa.Column("shelf", sa.String(30), nullable=False),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("total_copies", sa.Integer(), nullable=False),
        sa.Column("available_copies", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("total_copies > 0", name="ck_book_total"),
        sa.CheckConstraint("available_copies >= 0 AND available_copies <= total_copies", name="ck_book_available"))
    op.create_index("ix_books_title", "books", ["title"])
    op.create_index("ix_books_category", "books", ["category"])
    op.create_table("members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(180), nullable=False, unique=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("loans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id"), nullable=False),
        sa.Column("member_id", sa.Integer(), sa.ForeignKey("members.id"), nullable=False),
        sa.Column("borrowed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_loans_book_id", "loans", ["book_id"])
    op.create_index("ix_loans_member_id", "loans", ["member_id"])
    op.create_index("ix_loans_active_due", "loans", ["returned_at", "due_date"])


def downgrade():
    op.drop_table("loans")
    op.drop_table("members")
    op.drop_table("books")
