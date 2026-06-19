from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped
from core.database import AuditModel

class Tenant(AuditModel):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(125))
    code: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_deleted: Mapped[bool] = mapped_column(default=False)
