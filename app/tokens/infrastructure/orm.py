from sqlalchemy import Integer, Index
from sqlalchemy.orm import mapped_column, Mapped
from core.database import TenantAuditModelORM

class TokenORM(TenantAuditModelORM):

    __tablename__ = "tokens"

    __table_args__ = (
        Index("ix_tokens_tenant_id", "tenant_id"),
    )

    token_number: Mapped[int] = mapped_column(Integer)