from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, func, ForeignKey, MetaData
from sqlalchemy.orm import sessionmaker, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from core.config import settings



engine = create_async_engine(
    url=settings.database_url,
    pool_size=10,
    max_overflow=20,
    echo=True
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):

    metadata = MetaData(naming_convention=convention)

class BaseModel(Base):

    __abstract__ = True
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), default=func.now())

class AuditModel(BaseModel):

    __abstract__ = True

    created_by_id: Mapped[datetime] = mapped_column(ForeignKey("users.id"))
    updated_by_id: Mapped[datetime | None] = mapped_column(ForeignKey("users.id"), nullable=True, default=None)


class NullableAuditModel(BaseModel):
    __abstract__ = True

    created_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True, default=None)
    updated_by_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True, default=None)

class TenantAuditModel(AuditModel):

    __abstract__ = True

    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"))

class TenantNullableAuditModel(NullableAuditModel):
    __abstract__ = True

    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.id"), nullable=True)


async def get_db_session() -> AsyncSessionLocal:
    async with AsyncSessionLocal() as session:
        yield session