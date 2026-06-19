from uuid import UUID
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Index
from sqlalchemy.orm import mapped_column, Mapped
from core.database import TenantAuditModel

class Bill(TenantAuditModel):

    __tablename__ = "bills"

    __table_args__ = (
        Index("ix_bills_tenant_id", "tenant_id"),
        Index("ix_bills_token_id", "token_id"),
    )

    bill_number: Mapped[str] = mapped_column(String(50), unique=True)
    token_id: Mapped[UUID] = mapped_column(ForeignKey("tokens.id", ondelete="RESTRICT"))
    tax_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    sub_total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
