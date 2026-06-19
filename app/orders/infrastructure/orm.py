from uuid import UUID
from datetime import datetime
from decimal import Decimal
from sqlalchemy import ForeignKey, Index, DateTime
from sqlalchemy import Numeric, Boolean, SmallInteger
from sqlalchemy.orm import mapped_column, Mapped
from core.database import TenantAuditModel

class Order(TenantAuditModel):

    __tablename__ = "orders"

    __table_args__ = (
        Index("ix_orders_tenant_id", "tenant_id"),
        Index("ix_orders_token_id", "token_id"),
        Index("ix_orders_item_id", "item_id"),
    )

    item_id: Mapped[UUID] = mapped_column(ForeignKey("items.id", ondelete="RESTRICT"))
    token_id: Mapped[UUID] = mapped_column(ForeignKey("tokens.id", ondelete="RESTRICT"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[int] = mapped_column(SmallInteger)
    ordered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))