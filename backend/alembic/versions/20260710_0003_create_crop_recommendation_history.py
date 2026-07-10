"""create crop recommendation history

Revision ID: 20260710_0003
Revises: 20260710_0002
Create Date: 2026-07-10 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260710_0003"
down_revision = "20260710_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_recommendation_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farmer_id", sa.Integer(), nullable=False),
        sa.Column("nitrogen", sa.Numeric(10, 2), nullable=False),
        sa.Column("phosphorus", sa.Numeric(10, 2), nullable=False),
        sa.Column("potassium", sa.Numeric(10, 2), nullable=False),
        sa.Column("temperature", sa.Numeric(10, 2), nullable=False),
        sa.Column("humidity", sa.Numeric(10, 2), nullable=False),
        sa.Column("ph", sa.Numeric(4, 2), nullable=False),
        sa.Column("rainfall", sa.Numeric(10, 2), nullable=False),
        sa.Column("recommended_crop", sa.String(length=100), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.farmer_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_crop_recommendation_history_farmer_id"), "crop_recommendation_history", ["farmer_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_crop_recommendation_history_farmer_id"), table_name="crop_recommendation_history")
    op.drop_table("crop_recommendation_history")