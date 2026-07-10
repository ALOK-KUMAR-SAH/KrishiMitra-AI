"""create disease detection history

Revision ID: 20260710_0004
Revises: 20260710_0003
Create Date: 2026-07-10 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260710_0004"
down_revision = "20260710_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "disease_detection_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farmer_id", sa.Integer(), nullable=False),
        sa.Column("image_path", sa.String(length=512), nullable=False),
        sa.Column("crop_name", sa.String(length=100), nullable=False),
        sa.Column("predicted_disease", sa.String(length=100), nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False),
        sa.Column("recommended_solution", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.farmer_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_disease_detection_history_farmer_id"), "disease_detection_history", ["farmer_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_disease_detection_history_farmer_id"), table_name="disease_detection_history")
    op.drop_table("disease_detection_history")