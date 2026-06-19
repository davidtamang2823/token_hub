from sqlalchemy import Integer, Index
from sqlalchemy.orm import mapped_column, Mapped
from core.database import TenantAuditModel

class Token(TenantAuditModel):

    __tablename__ = "tokens"

    __table_args__ = (
        Index("ix_tokens_tenant_id", "tenant_id"),
    )

    token_number: Mapped[int] = mapped_column(Integer)