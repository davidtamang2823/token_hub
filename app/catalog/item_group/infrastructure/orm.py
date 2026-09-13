from uuid import UUID
from decimal import Decimal
from sqlalchemy import Numeric, Boolean, String, Index, UniqueConstraint, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from core.database import TenantAuditModelORM


class ItemGroupORM(TenantAuditModelORM):

    __tablename__ = "item_groups"

    __table_args__ = (
        Index("ix_item_groups_tenant_id", "tenant_id"),
        UniqueConstraint("tenant_id", "name")
    )

    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(String(500), nullable=True, default=None)
    category_id: Mapped[UUID] = mapped_column(ForeignKey("categories.id"))
