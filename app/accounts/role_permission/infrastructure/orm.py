import typing
from uuid import UUID
from sqlalchemy import ForeignKey, UniqueConstraint, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


from core.database import NullableAuditModel, Base, TenantNullableAuditModel

class Role(TenantNullableAuditModel):

    __tablename__ = "roles"

    __table_args__ = (
        UniqueConstraint("name", "tenant_id", name="uq_role_name_tenant_id"),
        Index("ix_roles_tenant_id", "tenant_id"),
    )

    name: Mapped[str] = mapped_column(String(75))
    is_system_role: Mapped[bool] = mapped_column(default=False)
    permissions: Mapped[typing.List["Permission"]] = relationship(secondary="role_permissions", back_populates="roles")

class Permission(NullableAuditModel):

    __tablename__ = "permissions"


    codename: Mapped[str] = mapped_column(String(75), unique=True)
    name: Mapped[str] = mapped_column(String(75), unique=True)
    description: Mapped[str] = mapped_column(String(500))
    roles: Mapped[typing.List["Role"]] = relationship(secondary="role_permissions", back_populates="permissions")


class RolePermission(Base):

    __tablename__ = "role_permissions"

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_id_permission_id"),
    )

    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
