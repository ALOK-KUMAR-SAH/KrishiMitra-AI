"""create marketplace listings

Revision ID: 20260710_0008
Revises: 20260710_0007
Create Date: 2026-07-10 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260710_0008"
down_revision = "20260710_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "marketplace_listings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("farmer_id", sa.Integer(), nullable=False),
        sa.Column("crop_name", sa.String(length=100), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=False),
        sa.Column("quantity_unit", sa.String(length=20), nullable=False),
        sa.Column("expected_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("quality_grade", sa.String(length=1), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("harvest_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'available'")),
        sa.Column("image_path", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.farmer_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_marketplace_listings_farmer_id"), "marketplace_listings", ["farmer_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_marketplace_listings_farmer_id"), table_name="marketplace_listings")
    op.drop_table("marketplace_listings")