"""Alter table permission change column names name, display_name to codename, name and added code field to tenant table

Revision ID: ec6024a67283
Revises: 4f92809c8e64
Create Date: 2026-06-16 03:11:36.487288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec6024a67283'
down_revision: Union[str, Sequence[str], None] = '4f92809c8e64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("permissions", "name", new_column_name="codename")
    op.alter_column("permissions", "display_name", new_column_name="name")

    op.drop_constraint("uq_permissions_name", "permissions", type_="unique")
    op.create_unique_constraint(op.f("uq_permissions_codename"), "permissions", ["codename"])
    op.create_unique_constraint(op.f("uq_permissions_name"), "permissions", ["name"])

    op.add_column("tenants", sa.Column("code", sa.String(length=20), nullable=False))
    op.create_unique_constraint(op.f("uq_tenants_code"), "tenants", ["code"])


def downgrade() -> None:
    op.drop_constraint(op.f("uq_tenants_code"), "tenants", type_="unique")
    op.drop_column("tenants", "code")

    op.drop_constraint(op.f("uq_permissions_name"), "permissions", type_="unique")
    op.drop_constraint(op.f("uq_permissions_codename"), "permissions", type_="unique")

    op.alter_column("permissions", "name", new_column_name="display_name")
    op.alter_column("permissions", "codename", new_column_name="name")

    op.create_unique_constraint(op.f("uq_permissions_name"), "permissions", ["name"])
