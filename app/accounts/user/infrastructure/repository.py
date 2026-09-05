import abc
from uuid import UUID
from sqlalchemy import select, exists, delete, or_, func, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.user.infrastructure import orm as user_orm
from accounts.role_permission.infrastructure import orm as role_permission_orm
from accounts.user.domain import models as user_domain
from accounts.user.domain.enumns.email_change_request_enum import EmailChangeRequestEnum
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
    async def list_user(self, user_filters: dict, limit: int, offset: int, exclude_id: UUID | None = None) -> list[user_domain.UserModel]:
        ...

    @abc.abstractmethod
    async def get_user_by_permission_name(self, permission_name: str, tenant_id: UUID | None) -> list[read_models.UserReadModel]:...

    @abc.abstractmethod
    async def get_user_email_request(self, user_id: UUID) -> user_domain.EmailChangeRequestModel | None: ...


    @abc.abstractmethod
    async def get_user_email_request_by_token(self, new_email_verification_token: str) -> user_domain.EmailChangeRequestModel | None: ...


    @abc.abstractmethod
    async def get_role_count_by_name(self, role_name: str, tenant_id: UUID | None, exclude_id: UUID = None) -> int: ...


    @abc.abstractmethod
    async def email_exists(self, email: str) -> bool:
        ...

    @abc.abstractmethod
    async def exists_in_tenant(self,  user_id:UUID, tenant_id: UUID) -> bool:
        ...

    # @abc.abstractmethod
    # async def exists_tenant_id(self, tenant_id: UUID) -> bool:
    #     ...

    @abc.abstractmethod
    async def user_exists_in_tenant(self, user_id: UUID, tenant_id: UUID) -> bool: ...

    @abc.abstractmethod
    async def role_already_assigned_to_user(self, role_id: UUID) -> bool: ...

    @abc.abstractmethod
    async def create_user(self, user: user_domain.UserModel) -> user_domain.UserModel: ...

    @abc.abstractmethod
    async def save_user_email_request(self, user_email_request: user_domain.EmailChangeRequestModel) -> None: ...

    @abc.abstractmethod
    async def add_user_to_tenant(self, user_tenant: user_domain.UserTenantModel) -> None: ...

    @abc.abstractmethod
    async def update_user(self, user: user_domain.UserModel) -> user_domain.UserModel: ...

    @abc.abstractmethod
    async def update_user_profile(self, user_id: UUID, first_name: str, last_name: str) -> None: ...

    @abc.abstractmethod
    async def update_user_status(self, user_id: UUID, is_active: bool) -> None: ...

    @abc.abstractmethod
    async def update_user_email(self, user_id: UUID, new_email: str) -> None: ...

    @abc.abstractmethod
    async def update_user(self, user: user_domain.UserModel) -> user_domain.UserModel: ...

    @abc.abstractmethod
    async def update_all_assigned_tenant_role(self, user_id: UUID, role_id: UUID) -> None: ...

    @abc.abstractmethod
    async def update_assigned_tenant_role(self, user_id: UUID, role_id: UUID, tenant_id: UUID) -> None: ...

    @abc.abstractmethod
    async def remove_user_from_tenant(self, user_id: UUID, tenant_id: UUID) -> None: ...

    @abc.abstractmethod
    async def delete_user(self, user_id: UUID) -> None: ...

    @abc.abstractmethod
    async def remove_user_from_all_tenant(self, user_id: UUID) -> None: ...

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
                role_permission_orm.RoleORM.name.label("role_name"),
                user_orm.UserORM.verified_at,
                user_orm.UserORM.is_deleted,
                user_orm.EmailChangeRequestORM.new_email.label("pending_email_change_request"),
                user_orm.EmailChangeRequestORM.status.label("pending_email_change_request_status")
            )
            .outerjoin(user_orm.UserTenantORM, user_orm.UserORM.id == user_orm.UserTenantORM.user_id)
            .outerjoin(role_permission_orm.RoleORM, user_orm.UserTenantORM.role_id == role_permission_orm.RoleORM.id)
            .outerjoin(
                user_orm.EmailChangeRequestORM, 
                and_(
                    user_orm.EmailChangeRequestORM.user_id == user_orm.UserORM.id,
                    user_orm.EmailChangeRequestORM.status == EmailChangeRequestEnum.PENDING.value,
                    user_orm.EmailChangeRequestORM.created_at > func.now() - user_domain.EMAIL_CHANGE_REQUEST_TTL,
                )
            )
            .where(user_orm.UserTenantORM.tenant_id == tenant_id, user_orm.UserORM.id == user_id)
            .distinct()
        )
        result = await self._session.execute(stmt)
        user_orm_obj = result.fetchone()
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
                verified_at=user_orm_obj.verified_at,
                is_deleted=user_orm_obj.is_deleted,
                pending_email_change_request=user_orm_obj.pending_email_change_request,
                pending_email_change_request_status=EmailChangeRequestEnum(user_orm_obj.pending_email_change_request_status).name if user_orm_obj.pending_email_change_request_status else None
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


    async def list_user(self, user_filters: dict, limit: int, offset: int, exclude_id: UUID | None = None) -> tuple[int, list[read_models.UserReadModel]]:
        
        tenant_id = user_filters.get("tenant_id")
        is_staff = user_filters.get("is_staff")
        is_active = user_filters.get("is_active")
        search_key = user_filters.get("q")
        drop_down = user_filters.get("drop_down")

        stmt = (
            select(
                user_orm.UserORM.id,
                user_orm.UserORM.first_name,
                user_orm.UserORM.last_name,
                user_orm.UserORM.email,
                user_orm.UserORM.is_active,
                user_orm.UserORM.is_staff,
                user_orm.UserTenantORM.role_id,
                role_permission_orm.RoleORM.name.label("role_name"),
                user_orm.UserORM.verified_at,
                user_orm.UserORM.is_deleted,
                user_orm.EmailChangeRequestORM.new_email.label("pending_email_change_request"),
                user_orm.EmailChangeRequestORM.status.label("pending_email_change_request_status")
            )
            .outerjoin(user_orm.UserTenantORM, user_orm.UserORM.id == user_orm.UserTenantORM.user_id)
            .outerjoin(role_permission_orm.RoleORM, user_orm.UserTenantORM.role_id == role_permission_orm.RoleORM.id)
            .outerjoin(
                user_orm.EmailChangeRequestORM, 
                and_(
                    user_orm.EmailChangeRequestORM.user_id == user_orm.UserORM.id,
                    user_orm.EmailChangeRequestORM.status == EmailChangeRequestEnum.PENDING.value,
                    user_orm.EmailChangeRequestORM.created_at > func.now() - user_domain.EMAIL_CHANGE_REQUEST_TTL,
                ),
            )
        )

        stmt = stmt.where(user_orm.UserORM.is_deleted == False)

        if tenant_id:
            stmt = stmt.where(user_orm.UserTenantORM.tenant_id == tenant_id)

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

        if exclude_id:
            stmt = stmt.where(user_orm.UserORM.id != exclude_id)

        total_count_stmt = (
            select(func.count()).select_from(stmt.subquery())
        )
        total = (await self._session.execute(total_count_stmt)).scalar()

        stmt = stmt.order_by(user_orm.UserORM.first_name, user_orm.UserORM.last_name, user_orm.UserORM.email).distinct()

        if not drop_down:
            stmt = stmt.offset(offset).limit(limit)


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
                verified_at=user_orm_obj.verified_at,
                is_deleted=user_orm_obj.is_deleted,
                pending_email_change_request=user_orm_obj.pending_email_change_request,
                pending_email_change_request_status=EmailChangeRequestEnum(user_orm_obj.pending_email_change_request_status).name if user_orm_obj.pending_email_change_request_status else None
            )
            for user_orm_obj in result.fetchall()
        ]

        return total, users

    async def get_user_by_permission_name(self, permission_name: str, tenant_id: UUID | None) -> list[read_models.UserReadModel]:

        stmt = (
            select(
                user_orm.UserORM.id,
                user_orm.UserORM.email,
                user_orm.UserORM.first_name,
                user_orm.UserORM.last_name,
                user_orm.UserORM.is_active,
                user_orm.UserORM.is_staff,
                user_orm.UserTenantORM.role_id,
                role_permission_orm.RoleORM.name.label("role_name"),
                user_orm.UserORM.verified_at,
                user_orm.UserORM.is_deleted
            )
            .join(user_orm.UserTenantORM, user_orm.UserORM.id == user_orm.UserTenantORM.user_id)
            .join(role_permission_orm.RoleORM, user_orm.UserTenantORM.role_id == role_permission_orm.RoleORM.id)
            .join(role_permission_orm.RolePermissionORM, role_permission_orm.RoleORM.id == role_permission_orm.RolePermissionORM.role_id)
            .join(role_permission_orm.PermissionORM, role_permission_orm.RolePermissionORM.permission_id == role_permission_orm.PermissionORM.id)
            .where(user_orm.UserTenantORM.tenant_id == tenant_id, role_permission_orm.PermissionORM.codename == permission_name, user_orm.UserORM.is_deleted == False)
            .distinct(user_orm.UserORM.id)
        )


        result = await self._session.execute(stmt)

        return [

            read_models.UserReadModel(
                id = user_orm_obj.id,
                email = user_orm_obj.email,
                first_name = user_orm_obj.first_name,
                last_name = user_orm_obj.last_name,
                is_active = user_orm_obj.is_active,
                is_staff=user_orm_obj.is_staff,
                role_id=user_orm_obj.role_id,
                role_name=user_orm_obj.role_name,
                verified_at=user_orm_obj.verified_at,
                is_deleted=user_orm_obj.is_deleted
            )
            for user_orm_obj in result.fetchall()
        ]


    async def get_user_email_request(self, user_id: UUID) -> user_domain.EmailChangeRequestModel | None:

        stmt = (
            select(user_orm.EmailChangeRequestORM)
            .where(
                user_orm.EmailChangeRequestORM.user_id == user_id,
                user_orm.EmailChangeRequestORM.status == EmailChangeRequestEnum.PENDING.value
            )
            .order_by(user_orm.EmailChangeRequestORM.created_at.desc())
        )
        result = await self._session.execute(stmt)
        user_email_request_orm_obj = result.scalars().first()

        if not user_email_request_orm_obj:
            return None

        return user_domain.EmailChangeRequestModel(
            id=user_email_request_orm_obj.id,
            old_email=user_email_request_orm_obj.old_email,
            new_email=user_email_request_orm_obj.new_email,
            user_id=user_email_request_orm_obj.user_id,
            new_email_verification_token=user_email_request_orm_obj.new_email_verification_token,
            new_email_verification_token_created_at=user_email_request_orm_obj.new_email_verification_token_created_at,
            status=user_domain.EmailChangeRequestEnum(user_email_request_orm_obj.status)
        )


    async def get_user_email_request_by_token(self, new_email_verification_token: str) -> user_domain.EmailChangeRequestModel | None:
        
        stmt = (
            select(user_orm.EmailChangeRequestORM)
            .where(
                user_orm.EmailChangeRequestORM.new_email_verification_token == new_email_verification_token,
                user_orm.EmailChangeRequestORM.status == EmailChangeRequestEnum.APPROVED.value
            )
        )
        result = await self._session.execute(stmt)
        user_email_request_orm_obj = result.scalar_one_or_none()

        if not user_email_request_orm_obj:
            return None

        return user_domain.EmailChangeRequestModel(
            id=user_email_request_orm_obj.id,
            old_email=user_email_request_orm_obj.old_email,
            new_email=user_email_request_orm_obj.new_email,
            user_id=user_email_request_orm_obj.user_id,
            new_email_verification_token=user_email_request_orm_obj.new_email_verification_token,
            new_email_verification_token_created_at=user_email_request_orm_obj.new_email_verification_token_created_at,
            status=user_domain.EmailChangeRequestEnum(user_email_request_orm_obj.status)
        )


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
                    user_orm.UserTenantORM.user_id == user_id
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

    async def get_role_count_by_name(self, role_name: str, tenant_id: UUID | None, exclude_id: UUID = None) -> int:
        stmt = (
            select(func.count(user_orm.UserORM.id))
            .join(user_orm.UserTenantORM, user_orm.UserTenantORM.user_id == user_orm.UserORM.id)
            .join(role_permission_orm.RoleORM, role_permission_orm.RoleORM.role_id == user_orm.UserTenantORM.role_id)
            .where(user_orm.UserTenantORM.tenant_id == tenant_id, role_permission_orm.RoleORM.name == role_name)
        )

        if exclude_id:
            stmt = stmt.where(user_orm.UserORM.id != exclude_id)

        result = await session.execute(stmt)
        count = result.scalar_one()
        return count


    async def create_user(self, user: user_domain.UserModel) -> user_domain.UserModel:

        user_orm_obj = user_orm.UserORM(
            id = user.id,
            first_name = user.first_name,
            last_name = user.last_name,
            is_active = user.is_active,
            password = user.hashed_password,
            is_deleted = user.is_deleted,
            is_staff = user.is_staff,
            email = user.email,
            verification_token = user.verification_token,
            verification_token_created_at = user.verification_token_created_at
        )

        self._session.add(user_orm_obj)
        await self._session.flush()
        return self._to_user_domain(user_orm_obj=user_orm_obj)


    async def save_user_email_request(self, user_email_request: user_domain.EmailChangeRequestModel) -> None:


        stmt = (
            select(
                user_orm.EmailChangeRequestORM
            )
            .where(
                user_orm.EmailChangeRequestORM.id == user_email_request.id
            )
        )

        user_email_request_orm_obj = (await self._session.execute(stmt)).scalar_one_or_none()
        if user_email_request_orm_obj is None:
            user_email_request_orm_obj = user_orm.EmailChangeRequestORM(
                id = user_email_request.id,
                user_id = user_email_request.user_id,
                old_email = user_email_request.old_email,
                new_email = user_email_request.new_email,
                tenant_id = user_email_request.tenant_id,
                created_by_id = user_email_request.created_by_id,
            )
            self._session.add(user_email_request_orm_obj)

        user_email_request_orm_obj.status = user_email_request.status.value
        user_email_request_orm_obj.new_email_verification_token = user_email_request.new_email_verification_token
        user_email_request_orm_obj.new_email_verification_token_created_at = user_email_request.new_email_verification_token_created_at
        user_email_request_orm_obj.updated_by_id = user_email_request.updated_by_id
        




    async def add_user_to_tenant(self, user_tenant: user_domain.UserTenantModel) -> None:

        user_tenant_orm_obj = user_orm.UserTenantORM(
            user_id = user_tenant.user_id,
            role_id = user_tenant.role_id,
            tenant_id = user_tenant.tenant_id,
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


    async def update_user_status(self, user_id: UUID, is_active: bool) -> None:
        
        stmt = (
            update(user_orm.UserORM)
            .where(user_orm.UserORM.id == user_id)
            .values(is_active=is_active)
        )
        await self._session.execute(stmt)


    async def update_user_email(self, user_id: UUID, new_email: str) -> None:

        stmt = (
            update(
                user_orm.UserORM
            )
            .where(
                user_orm.UserORM.id == user_id
            )
            .values(
                email = new_email
            )
        )
        await self._session.execute(stmt)


    async def update_user(self, user: user_domain.UserModel) -> user_domain.UserModel:

        stmt = (
            select(user_orm.UserORM)
            .where(user_orm.UserORM.id == user.id)
        )

        user_orm_obj = (await self._session.execute(stmt)).scalar_one_or_none()

        if not user_orm_obj:
            return None

        user_orm_obj.first_name = user.first_name
        user_orm_obj.last_name = user.last_name
        user_orm_obj.is_active = user.is_active
        user_orm_obj.is_deleted = user.is_deleted
        user_orm_obj.verification_token = user.verification_token
        user_orm_obj.verification_token_created_at = user.verification_token_created_at
        user_orm_obj.is_staff = user.is_staff
        user_orm_obj.verified_at = user.verified_at
        if user.hashed_password:
            user_orm_obj.password = user.hashed_password

        return self._to_user_domain(user_orm_obj=user_orm_obj)


    async def update_all_assigned_tenant_role(self, user_id: UUID, role_id: UUID) -> None:

        stmt = (
            update(user_orm.UserTenantORM)
            .where(user_orm.UserTenantORM.user_id == user_id)
            .values(role_id = role_id)
        )

        await self._session.execute(stmt)

    async def update_assigned_tenant_role(self, user_id: UUID, role_id: UUID, tenant_id: UUID) -> None:

        stmt = (
            update(user_orm.UserTenantORM)
            .where(user_orm.UserTenantORM.user_id == user_id, user_orm.UserTenantORM.tenant_id == tenant_id)
            .values(role_id = role_id)
        )

        await self._session.execute(stmt)

    async def remove_user_from_tenant(self, user_id: UUID, tenant_id: UUID) -> None:

        stmt = (
            delete(user_orm.UserTenantORM)
            .where(user_orm.UserTenantORM.user_id == user_id, user_orm.UserTenantORM.tenant_id == tenant_id)
        )

        await self._session.execute(stmt)


    async def delete_user(self, user_id: UUID) -> None:

        stmt = (
            update(user_orm.UserORM)
            .where(user_orm.UserORM.id == user_id)
            .values(is_deleted = True)
        )

        await self._session.execute(stmt)

    async def remove_user_from_all_tenant(self, user_id: UUID) -> None:

        stmt = (
            delete(
                user_orm.UserTenantORM
            )
            .where(user_orm.UserTenantORM.user_id == user_id)
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
            email=user_orm_obj.email,
            is_deleted=user_orm_obj.is_deleted,
            verified_at=user_orm_obj.verified_at
        )