"""create shelf life prediction history

Revision ID: 20260710_0006
Revises: 20260710_0005
Create Date: 2026-07-10 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260710_0006"
down_revision = "20260710_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shelf_life_prediction_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farmer_id", sa.Integer(), nullable=False),
        sa.Column("crop_name", sa.String(length=100), nullable=False),
        sa.Column("harvest_date", sa.Date(), nullable=False),
        sa.Column("storage_type", sa.String(length=100), nullable=False),
        sa.Column("temperature", sa.Numeric(5, 2), nullable=False),
        sa.Column("humidity", sa.Numeric(5, 2), nullable=False),
        sa.Column("predicted_shelf_life_days", sa.Integer(), nullable=False),
        sa.Column("remaining_days", sa.Integer(), nullable=False),
        sa.Column("freshness_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.farmer_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_shelf_life_prediction_history_farmer_id"), "shelf_life_prediction_history", ["farmer_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_shelf_life_prediction_history_farmer_id"), table_name="shelf_life_prediction_history")
    op.drop_table("shelf_life_prediction_history")