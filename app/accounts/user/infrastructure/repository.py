import abc
from uuid import UUID
from sqlalchemy import select, exists, delete, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.user.infrastructure import orm as user_orm
from accounts.role_permission.infrastructure import orm as role_permission_orm
from accounts.user.domain import models as user_domain
from accounts.user.application import read_models

class AbstractUserRepository(abc.ABC):


    @abc.abstractmethod
    async def get_by_id(self, user_id: UUID) -> user_domain.UserModel | None:
        ...

    @abc.abstractmethod
    async def get_by_email(self, email: str) -> user_domain.UserModel | None:
        ...

    @abc.abstractmethod
    async def get_user_with_role(self, user_id: UUID, tenant_id: UUID) -> read_models.UserReadModel | None:
        ...

    @abc.abstractmethod
    async def list_user(self, user_filters: dict, limit: int, offset: int) -> list[user_domain.UserModel]:
        ...

    @abc.abstractmethod
    async def email_exists(self, email: str) -> bool:
        ...

    @abc.abstractmethod
    async def exists_in_tenant(self,  user_id:UUID, tenant_id: UUID) -> bool:
        ...

    @abc.abstractmethod
    async def exists_tenant_id(self, tenant_id: UUID) -> bool:
        ...

    @abc.abstractmethod
    async def user_exists_in_tenant(self, user_id: UUID, tenant_id: UUID) -> bool: ...

    @abc.abstractmethod
    async def role_already_assigned_to_user(self, role_id: UUID) -> bool: ...

    @abc.abstractmethod
    async def create_user(self, user: user_domain.UserModel) -> user_domain.UserModel: ...

    @abc.abstractmethod
    async def add_user_to_tenant(self, user_tenant: user_domain.UserTenantModel) -> None: ...


    @abc.abstractmethod
    async def update_user_profile(self, user_id: UUID, first_name: str, last_name: str) -> None: ...

    @abc.abstractmethod
    async def remove_user_from_tenant(self, user_id: UUID, tenant_id: UUID) -> None: ...

class UserRepository(AbstractUserRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: UUID) -> user_domain.UserModel | None:
        stmt = (
            select(user_orm.UserORM)
            .where(user_orm.UserORM.id == user_id)
        )
        result = await self._session.execute(stmt)
        user_orm_obj = result.scalar_one_or_none()
        return self._to_user_domain(user_orm_obj)


    async def get_user_with_role(self, user_id: UUID, tenant_id: UUID) -> read_models.UserReadModel | None:

        stmt = (
            select(
                user_orm.UserORM.id,
                user_orm.UserORM.first_name,
                user_orm.UserORM.last_name,
                user_orm.UserORM.email,
                user_orm.UserORM.is_active,
                user_orm.UserORM.is_staff,
                user_orm.UserTenantORM.role_id,
                role_permission_orm.Role.name.label("role_name"),
                user_orm.UserORM.verified_at
            )
            .join(user_orm.UserTenantORM, user_orm.UserORM.id == user_orm.UserTenantORM.user_id)
            .join(role_permission_orm.Role, user_orm.UserTenantORM.role_id == role_permission_orm.Role.id)
            .where(user_orm.UserTenantORM.tenant_id == tenant_id)
            .where(user_orm.UserORM.id == user_id)
        )
        result = await self._session.execute(stmt)
        user_orm_obj = result.scalar_one_or_none()
        return (
            read_models.UserReadModel(
                id = user_orm_obj.id,
                email = user_orm_obj.email,
                first_name = user_orm_obj.first_name,
                last_name = user_orm_obj.last_name,
                is_active = user_orm_obj.is_active,
                is_staff=user_orm_obj.is_staff,
                role_id=user_orm_obj.role_id,
                role_name=user_orm_obj.role_name,
                verified_at=user_orm_obj.verified_at
            ) if user_orm_obj else None
        )

    async def get_by_email(self, email: str) -> user_domain.UserModel | None:
        stmt = (
            select(user_orm.UserORM)
            .where(user_orm.UserORM.email == email)
        )
        result = await self._session.execute(stmt)
        user_orm_obj = result.scalar_one_or_none()
        return self._to_user_domain(user_orm_obj)


    async def list_user(self, user_filters: dict, limit: int, offset: int) -> tuple[int, list[read_models.UserReadModel]]:
        
        tenant_id = user_filters.get("tenant_id")
        is_staff = user_filters.get("is_staff")
        is_active = user_filters.get("is_active")
        search_key = user_filters.get("q")

        stmt = (
            select(
                user_orm.UserORM.id,
                user_orm.UserORM.first_name,
                user_orm.UserORM.last_name,
                user_orm.UserORM.email,
                user_orm.UserORM.is_active,
                user_orm.UserORM.is_staff,
                user_orm.UserTenantORM.role_id,
                role_permission_orm.Role.name.label("role_name"),
                user_orm.UserORM.verified_at
            )
            .join(user_orm.UserTenantORM, user_orm.UserORM.id == user_orm.UserTenantORM.user_id)
            .join(role_permission_orm.Role, user_orm.UserTenantORM.role_id == role_permission_orm.Role.id)
            .where(user_orm.UserTenantORM.tenant_id == tenant_id)
        )

        if is_staff is not None:
            stmt = stmt.where(user_orm.UserORM.is_staff == is_staff)

        if is_active is not None:
            stmt = stmt.where(user_orm.UserORM.is_active == is_active)

        if search_key:
            stmt = stmt.where(
                or_(
                    user_orm.UserORM.first_name.istartswith(search_key),
                    user_orm.UserORM.last_name.istartswith(search_key),
                    user_orm.UserORM.email.istartswith(search_key)
                )
            )

        total_count_stmt = (
            select(func.count()).select_from(stmt.subquery())
        )
        total = (await self._session.execute(total_count_stmt)).scalar()

        stmt = stmt.order_by(user_orm.UserORM.first_name, user_orm.UserORM.last_name, user_orm.UserORM.email).distinct().offset(offset).limit(limit)

        result = await self._session.execute(stmt)

        users = [
            read_models.UserReadModel(
                id = user_orm_obj.id,
                email = user_orm_obj.email,
                first_name = user_orm_obj.first_name,
                last_name = user_orm_obj.last_name,
                is_active = user_orm_obj.is_active,
                is_staff=user_orm_obj.is_staff,
                role_id=user_orm_obj.role_id,
                role_name=user_orm_obj.role_name,
                verified_at=user_orm_obj.verified_at
            )
            for user_orm_obj in result.fetchall()
        ]

        return total, users



    async def email_exists(self, email: str) -> bool:

        stmt = (
            select(
                exists()
                .where(user_orm.UserORM.email == email)
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def exists_in_tenant(self,  user_id:UUID, tenant_id: UUID) -> bool:
        stmt = select(
            exists()
            .where(
                user_orm.UserTenantORM.user_id == user_id,
                user_orm.UserTenantORM.tenant_id == tenant_id
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar()

    async def user_exists_in_tenant(self, user_id: UUID, tenant_id: UUID) -> bool:

        stmt = (
            select(
                exists()
                .where(
                    user_orm.UserTenantORM.tenant_id == tenant_id,
                    user_orm.UserTenantORM.role_id == role_id
                )
            )
        )

        result = await self._session.execute(stmt)
        return result.scalar()

    async def role_already_assigned_to_user(self, role_id: UUID) -> bool:

        stmt = select(
            exists()
            .where(
                user_orm.UserTenantORM.role_id == role_id
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar()


    async def create_user(self, user: user_domain.UserModel) -> user_domain.UserModel:

        user_orm_obj = user_orm.UserORM(
            id = user.id,
            first_name = user.first_name,
            last_name = user.last_name,
            is_active = user.is_active,
            is_staff = user.is_staff,
            email = user.email,
            verification_token = user.verification_token,
            verification_token_created_at = user.verification_token_created_at
        )

        self._session.add(user_orm_obj)
        self._session.flush()
        return self._to_user_domain(user_orm_obj=user_orm_obj)


    async def add_user_to_tenant(self, user_tenant: user_domain.UserTenantModel) -> None:

        user_tenant_orm_obj = user_orm.UserTenantORM(
            user_id = user_tenant.user_id,
            role_id = user_tenant.role_id,
            created_by_id = user_tenant.created_by_id
        )

        self._session.add(user_tenant_orm_obj)

    async def update_user_profile(self, user_id: UUID, first_name: str, last_name: str) -> None:

        stmt = (
            update(user_orm.UserORM)
            .where(user_orm.UserORM.id == user_id)
            .values(first_name=first_name, last_name=last_name)
        )
        await self._session.execute(stmt)

    async def remove_user_from_tenant(self, user_id: UUID, tenant_id: UUID) -> None:

        stmt = (
            delete(user_orm.UserTenantORM)
            .where(user_orm.UserTenantORM.user_id == user_id, user_orm.UserTenantORM.tenant_id == tenant_id)
        )

        await self._session.execute(stmt)

    def _to_user_domain(self, user_orm_obj: user_orm.UserORM) -> user_domain.UserModel | None:
        if not user_orm_obj:
            return None

        return user_domain.UserModel(
            id=user_orm_obj.id,
            first_name=user_orm_obj.first_name,
            last_name=user_orm_obj.last_name,
            is_active=user_orm_obj.is_active,
            is_staff=user_orm_obj.is_staff,
            email=user_orm_obj.email
        )