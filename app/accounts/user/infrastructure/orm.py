import typing
from uuid import UUID
from datetime import datetime
from sqlalchemy import DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import NullableAuditModel, TenantNullableAuditModel


class User(NullableAuditModel):

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(String(225))
    first_name: Mapped[str | None] = mapped_column(String(125), default=None, nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(125), default=None, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False)
    is_staff: Mapped[bool] = mapped_column(default=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    verification_token: Mapped[str] = mapped_column(String(64),nullable=True, default=None)
    verification_token_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True, default=None)

    tenants: Mapped[typing.List["Tenant"]] = relationship(
        secondary="user_tenants",
        primaryjoin="User.id == UserTenant.user_id",
        secondaryjoin="UserTenant.tenant_id == Tenant.id",
        viewonly=True
    )

class UserTenant(TenantNullableAuditModel):

    __tablename__ = "user_tenants"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"))
    is_default: Mapped[bool] = mapped_column(default=False)