import abc
import typing
import secrets
import datetime
from uuid import UUID
from core.unit_of_work import UnitOfWork
from core.context import CurrentUser
from core.pagination import Pagination
from core.constants.permissions import CAN_VIEW_ALL_TENANT
from accounts.user.domain import models as user_domain
from core.exceptions import NotFoundException, AlreadyExistsException, ForbiddenException
from accounts.role_permission.application.policies import TenantAccessPolicy
from accounts.user.application import dtos as user_dtos
from accounts.user.application import read_models

class AbstractUserService(abc.ABC):

    @abc.abstractmethod
    async def list_user(self, user_filters: dict, page: int, page_size: int) -> Pagination: ...

    @abc.abstractmethod
    async def retrive_user(self, user_id: UUID) -> read_models.UserReadModel: ...

    @abc.abstractmethod
    async def add_user_to_tenant(self, data: typing.Dict): ...
    
    @abc.abstractmethod
    async def request_user_email_change(self, email: str) -> None: ...

    @abc.abstractmethod
    async def update_user_name(self, user_dto: user_dtos.UpdateUserName) -> None: ...

    @abc.abstractmethod
    async def update_user_status(self, user_dto: user_dtos.UpdateUserStatus) -> None: ...

    @abc.abstractmethod
    async def remove_user_from_tenant(self, data: typing.Dict): ...




class UserService(AbstractUserService):


    def __init__(self, uow: UnitOfWork, tenant_access_policy: TenantAccessPolicy, current_user: CurrentUser):
        self._uow = uow
        self._current_user = current_user
        self._tenant_access_policy = tenant_access_policy


    async def list_user(self, user_filters: dict, page: int, page_size: int) -> Pagination:

        
        if not user_filters.get("tenant_id"):
            user_filters["tenant_id"] = self._current_user.tenant_id
            user_filters["is_staff"] = self._current_user.is_staff
        else:
            self._tenant_access_policy.ensure_user_in_tenant(user_filters.get("tenant_id"))
        
        offset = (page - 1) * page_size

        total_count, users = await self._uow.user_repository.list_user(
            user_filters=user_filters,
            limit=page_size,
            offset=offset
        )

        return Pagination(
            page=page,
            page_size=page_size,
            total_count=total_count,
            data=users
        )

    async def retrive_user(self, user_id: UUI, tenant_id: UUID | None = None) -> read_models.UserReadModel:

        user = await self._uow.user_repository.get_user_with_role(
            user_id=user_id, 
            tenant_id=self._current_user.tenant_id if not tenant_id else tenant_id
        )
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return user

    async def _create_user(self, data: dict) -> user_domain.User:
        user = user_domain.User.create(
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email"),
            is_active=False,
            is_staff= data.get("is_staff") if self._current_user.is_staff else False,
            verification_token=secrets.token_urlsafe(32),
            verification_token_created_at=datetime.datetime.now(tz=datetime.timezone.utc)
        )
        await self._uow.user_repository.create_user(user=user)
        self._uow.register_entity(user)
        return user

    async def add_user_to_tenant(self, data: dict, tenant_id: UUID | None = None):
        
        email = data.get("email", "").strip()
        tenant_id = self._current_user.tenant_id if not tenant_id else tenant_id
        user = await self._uow.user_repository.get_by_email(email)
        
        
        existing_tenant = await self._uow.tenant_repository.get_tenant_by_id(tenant_id=tenant_id)
        
        if not existing_tenant:
            raise NotFoundException(f"Tenant with id {tenant_id} not found")

        self._tenant_access_policy.ensure_user_in_tenant(tenant_id)

        if not user:
            user = await self._create_user(data)
        
        user_tenant = user_domain.UserTenant.create(
            email=email,
            role_id=role_id,
            tenant_id=data.get("tenant_id"),
            tenant_name=existing_tenant.name,
            tenant_code=existing_tenant.code,
            created_by_id=self._current_user.id
        )

        if await self._uow.user_repository.user_exists_in_tenant(user.id, tenant_id):
            raise AlreadyExistsException("User already exists in tenant")

        await self._uow.user_repository.add_user_to_tenant(user_tenant=user_tenant)
        self._uow.register_entity(user_tenant)


    async def update_user_name(self, user_dto: user_dtos.UpdateUserName, user_id: UUID | None = None) -> read_models.UserReadModel:

        user_id = self._current_user.id if user_id is None else user_id

        if await self._uow.user_repository.is_user_in_tenant(user_id=user_id, tenant_id=self._current_user.tenant_id) is False:
            raise NotFoundException(f"User with id {user_id} not found")


        await self._uow.user_repository.update_user_profile(
            user_id=user_id,
            first_name=user_dto.first_name,
            last_name=user_dto.last_name
        )

        return await self._uow.user_repository.get_user_with_role(
            user_id=user_id, 
            tenant_id=self._current_user.tenant_id
        )


    async def update_user_status(self, user_dto: user_dtos.UpdateUserStatus) -> None:

        if not await self._uow.user_repository.is_user_in_tenant(user_id=user_dto.user_id, tenant_id=self._current_user.tenant_id):
            raise NotFoundException(f"User with id {user_dto.user_id} not found")

        await self._uow.user_repository.update_user_status(
            user_id=user_dto.user_id,
            is_active=user_dto.is_active
        )

    async def remove_user_from_tenant(self, user_id: UUID, tenant_id: UUID | None = None) -> None:

        tenant_id = self._current_user.tenant_id if not tenant_id else tenant_id

        
        if not await self._uow.tenant_repository.tenant_id_exists(tenant_id=tenant_id):
            raise NotFoundException(f"Tenant with id {tenant_id} not found")

        self._tenant_access_policy.ensure_user_in_tenant(tenant_id)


        await self._uow.user_repository.remove_user_from_tenant(user_id=user_id, tenant_id=tenant_id)