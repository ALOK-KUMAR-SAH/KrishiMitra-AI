"""create produce quality history

Revision ID: 20260710_0007
Revises: 20260710_0006
Create Date: 2026-07-10 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260710_0007"
down_revision = "20260710_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "produce_quality_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farmer_id", sa.Integer(), nullable=False),
        sa.Column("crop_name", sa.String(length=100), nullable=False),
        sa.Column("image_path", sa.String(length=512), nullable=False),
        sa.Column("grade", sa.String(length=1), nullable=False),
        sa.Column("quality_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("defects", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.farmer_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_produce_quality_history_farmer_id"), "produce_quality_history", ["farmer_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_produce_quality_history_farmer_id"), table_name="produce_quality_history")
    op.drop_table("produce_quality_history")