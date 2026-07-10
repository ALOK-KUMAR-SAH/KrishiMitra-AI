"""create farmers table

Revision ID: 20260710_0002
Revises: 20260710_0001
Create Date: 2026-07-10 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260710_0002"
down_revision = "20260710_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "farmers",
        sa.Column("farmer_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("aadhaar", sa.String(length=12), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("district", sa.String(length=100), nullable=False),
        sa.Column("village", sa.String(length=100), nullable=False),
        sa.Column("pincode", sa.String(length=10), nullable=False),
        sa.Column("farm_size", sa.Numeric(10, 2), nullable=False),
        sa.Column("soil_type", sa.String(length=100), nullable=False),
        sa.Column("primary_crop", sa.String(length=100), nullable=False),
        sa.Column("secondary_crop", sa.String(length=100), nullable=True),
        sa.Column("experience_years", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 6), nullable=False),
        sa.Column("longitude", sa.Numeric(10, 6), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("farmer_id"),
        sa.UniqueConstraint("user_id", name="uq_farmers_user_id"),
        sa.UniqueConstraint("aadhaar", name="uq_farmers_aadhaar"),
    )


def downgrade() -> None:
    op.drop_table("farmers")