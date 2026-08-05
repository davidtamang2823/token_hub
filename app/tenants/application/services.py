import abc
from uuid import UUID
from core.context import CurrentUser
from core.unit_of_work import UnitOfWork
from core.constants import permissions
from core.pagination import Pagination, DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from core.exceptions import NotFoundException, AlreadyExistsException, ForbiddenException
from tenants.domain.models import TenantModel
from accounts.role_permission.application.services import AbstractRolePermissionService
from accounts.role_permission.application.policies import TenantAccessPolicy

class AbstractTenantService(abc.ABC):


    @abc.abstractmethod
    async def list_tenant(self, tenant_filters: dict, page: int, page_size: int) -> Pagination: ...

    @abc.abstractmethod
    async def retrieve_tenant(self, tenant_id: UUID) -> TenantModel:  ...

    @abc.abstractmethod
    async def create_tenant(self, data: dict) -> TenantModel: ...

    @abc.abstractmethod
    async def update_tenant(self, data: dict) -> TenantModel: ...

    @abc.abstractmethod
    async def delete_tenant(self, tenant_id: UUID) -> None: ...



class TenantService(AbstractTenantService):


    def __init__(self, uow: UnitOfWork, role_perm_service: AbstractRolePermissionService, tenant_access_policy: TenantAccessPolicy, current_user: CurrentUser):
        self._uow = uow
        self._role_perm_service = role_perm_service
        self._current_user = current_user
        self._tenant_access_policy = tenant_access_policy

    async def list_tenant(self, tenant_filters: dict, page: int, page_size: int) -> Pagination:

        offset = (page - 1) * page_size

        if permissions.CAN_VIEW_ALL_TENANT in  self._current_user.permissions:
            tenant_filters["has_view_all_tenant_permission"] = True
        else:
            tenant_filters["user_id"] = self._current_user.id
    
        tenants, total = await self._uow.tenant_repository.list_tenant(
            tenant_filters=tenant_filters,
            offset=offset,
            limit=page_size
        )
        return Pagination(
            page = page,
            page_size = page_size,
            total = total,
            data = tenants
        )

    async def retrieve_tenant(self, tenant_id: UUID) -> TenantModel:
        
        self._tenant_access_policy.ensure_user_in_tenant(tenant_id=tenant_id)


        tenant = await self._uow.tenant_repository.get_tenant_by_id(
            tenant_id=tenant_id
        )

        if not tenant:
            raise NotFoundException(f"Tenant with id {tenant_id} not found")

        return tenant

    async def create_tenant(self, data: dict) -> TenantModel:
        tenant = TenantModel.create(
            name=data.get("name"),
            code=data.get("code"),
            is_active=data.get("is_active"),
            created_by_id=self._current_user.id
        )

        if await self._uow.tenant_repository.tenant_name_exists(tenant.name):
            raise AlreadyExistsException(f"Tenant with this name {tenant.name} already exists")
        if await self._uow.tenant_repository.tenant_code_exists(tenant.code):
            raise AlreadyExistsException(f"Tenant with this code {tenant.code} already exists")

        tenant = await self._uow.tenant_repository.create_tenant(tenant=tenant)
        await self._role_perm_service.create_default_roles_for_tenant(tenant_id=tenant.id)
        return tenant


    async def update_tenant(self, data: dict) -> TenantModel:

        tenant_id = data.get("id")

        self._tenant_access_policy.ensure_user_in_tenant(tenant_id=tenant_id)

        if not await self._uow.tenant_repository.tenant_id_exists(tenant_id=tenant_id):
            raise NotFoundException(f"Tenant with id {tenant_id} not found")

        tenant = TenantModel.update(
            tenant_id=data.get("id"),
            name=data.get("name"),
            code=data.get("code"),
            is_active=data.get("is_active"),
            updated_by_id=self._current_user.id
        )

        if await self._uow.tenant_repository.tenant_name_exists(tenant.name, exclude_tenant_id=tenant.id):
            raise AlreadyExistsException(f"Tenant with this name {tenant.name} already exists")
        if await self._uow.tenant_repository.tenant_code_exists(tenant.code, exclude_tenant_id=tenant.id):
            raise AlreadyExistsException(f"Tenant with this code {tenant.code} already exists")

        tenant = await self._uow.tenant_repository.update_tenant(tenant=tenant)
        return tenant

    async def delete_tenant(self, tenant_id: UUID) -> None:

        self._tenant_access_policy.ensure_user_in_tenant(tenant_id=tenant_id)

        if not await self._uow.tenant_repository.tenant_id_exists(tenant_id=tenant_id):
            raise NotFoundException(f"Tenant with id {tenant_id} not found")

        await self._uow.tenant_repository.delete_tenant(tenant_id=tenant_id)