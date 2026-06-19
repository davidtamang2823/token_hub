from decimal import Decimal
from sqlalchemy import Numeric, Boolean, String, Index
from sqlalchemy.orm import mapped_column, Mapped
from core.database import TenantAuditModel

class Item(TenantAuditModel):

    __tablename__ = "items"

    __table_args__ = (
        Index("ix_items_tenant_id", "tenant_id"),
    )

    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(String(500))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)