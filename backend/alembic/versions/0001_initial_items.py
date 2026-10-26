"""Initial schema migration: create items table for FindSpot Lost and Found."""

import sqlalchemy as sa
from alembic import op

revision = "0001_initial_items"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("category", sa.String(60), nullable=False),
        sa.Column("description", sa.String(500), server_default="", nullable=False),
        sa.Column("found_by", sa.String(120), nullable=False),
        sa.Column("finder_contact", sa.String(120), nullable=False),
        sa.Column("location_found", sa.String(150), nullable=False),
        sa.Column("collection_point", sa.String(60), nullable=False),
        sa.Column("status", sa.String(20), server_default="found", nullable=False),
        sa.Column("claimed_by", sa.String(120), nullable=True),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("found_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('found', 'claimed')", name="ck_item_status"),
    )
    op.create_index("ix_items_category", "items", ["category"])
    op.create_index("ix_items_collection_point", "items", ["collection_point"])
    op.create_index("ix_items_status", "items", ["status"])
    op.create_index("ix_items_status_category", "items", ["status", "category"])


def downgrade():
    op.drop_index("ix_items_status_category", table_name="items")
    op.drop_index("ix_items_status", table_name="items")
    op.drop_index("ix_items_collection_point", table_name="items")
    op.drop_index("ix_items_category", table_name="items")
    op.drop_table("items")
