"""change embedding dimension to 384

Revision ID: 20260913_phase3_vector
Revises: 20260913_phase2
Create Date: 2026-09-13 15:30:00.000000

"""

from alembic import op
from pgvector.sqlalchemy import Vector


revision = "20260913_phase3_vector"
down_revision = "20260913_phase2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "chunks",
        "embedding",
        existing_type=Vector(dim=1536),
        type_=Vector(dim=384),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "chunks",
        "embedding",
        existing_type=Vector(dim=384),
        type_=Vector(dim=1536),
        existing_nullable=True,
    )