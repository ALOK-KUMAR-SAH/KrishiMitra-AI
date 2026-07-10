"""create harvest prediction history

Revision ID: 20260710_0005
Revises: 20260710_0004
Create Date: 2026-07-10 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260710_0005"
down_revision = "20260710_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "harvest_prediction_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farmer_id", sa.Integer(), nullable=False),
        sa.Column("crop_name", sa.String(length=100), nullable=False),
        sa.Column("sowing_date", sa.Date(), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("predicted_harvest_date", sa.Date(), nullable=False),
        sa.Column("days_remaining", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.farmer_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_harvest_prediction_history_farmer_id"), "harvest_prediction_history", ["farmer_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_harvest_prediction_history_farmer_id"), table_name="harvest_prediction_history")
    op.drop_table("harvest_prediction_history")