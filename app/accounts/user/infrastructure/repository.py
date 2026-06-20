import abc
from uuid import UUID
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.user.infrastructure import orm as user_orm
from accounts.user.domain import models as user_domain

class AbstractUserRepository(abc.ABC):


    @abc.abstractmethod
    async def get_by_id(self, user_id: UUID) -> user_domain.User | None:
        ...

    @abc.abstractmethod
    async def get_by_email(self, email: str) -> user_domain.User | None:
        ...

    @abc.abstractmethod
    async def exists_in_tenant(self,  user_id:UUID, tenant_id: UUID) -> bool:
        ...

    @abc.abstractmethod
    async def role_already_assigned_to_user(self, role_id: UUID) -> bool: ...

class UserRepository(AbstractUserRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: UUID) -> user_domain.User | None:
        stmt = (
            select(user_orm.User)
            .where(user_orm.User.id == user_id)
        )
        result = await self._session.execute(stmt)
        user_orm_obj = result.scalar_one_or_none()
        return self._to_user_domain(user_orm_obj)

    async def get_by_email(self, email: str) -> user_domain.User | None:
        stmt = (
            select(user_orm.User)
            .where(user_orm.User.email == email)
        )
        result = await self._session.execute(stmt)
        user_orm_obj = result.scalar_one_or_none()
        return self._to_user_domain(user_orm_obj)

    async def exists_in_tenant(self,  user_id:UUID, tenant_id: UUID) -> bool:
        stmt = select(
            exists()
            .where(
                user_orm.UserTenant.user_id == user_id,
                user_orm.UserTenant.tenant_id == tenant_id
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def role_already_assigned_to_user(self, role_id: UUID) -> bool:

        stmt = select(
            exists()
            .where(
                user_orm.UserTenant.role_id == role_id
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    def _to_user_domain(self, user_orm_obj: user_orm.User) -> user_domain.User | None:
        if not user_orm_obj:
            return None

        return user_domain.User(
            id=user_orm_obj.id,
            first_name=user_orm_obj.first_name,
            last_name=user_orm_obj.last_name,
            is_active=user_orm_obj.is_active,
            is_staff=user_orm_obj.is_staff,
            email=user_orm_obj.email
        )