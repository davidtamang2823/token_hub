from decimal import Decimal
from sqlalchemy import Numeric, Boolean, String, Index, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped
from core.database import TenantAuditModelORM


class CategoryORM(TenantAuditModelORM):

    __tablename__ = "categories"

    __table_args__ = (
        Index("ix_categories_tenant_id", "tenant_id"),
        UniqueConstraint("tenant_id", "name")
    )

    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(String(500), nullable=True, default=None)
