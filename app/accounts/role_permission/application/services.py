import abc
from uuid import UUID
from accounts.role_permission.domain import models as role_permission_domain
from core.unit_of_work import UnitOfWork
from core.context import CurrentUser
from core.exceptions import NotFoundException, AlreadyExistsException, ResourceInUseError, ForbiddenException
from core.pagination import Pagination
from core.constants.roles import TENANT_DEFAULT_ROLES
from accounts.role_permission.presentation import schemas

class AbstractRolePermissionService(abc.ABC):


    @abc.abstractmethod
    async def retrieve_role(self, role_id: UUID) -> schemas.RolePermissionSchema: ...

    @abc.abstractmethod
    async def list_role(self, role_filters: dict, page: int, page_size: int)  -> Pagination: ...

    @abc.abstractmethod
    async def list_role_option(self, page: int, page_size: int, tenant_id: UUID)  -> schemas.ListRoleOptionSchema: ...

    @abc.abstractmethod
    async def list_permission(self, permission_filters: dict) -> schemas.ListPermissionSchema: ...

    @abc.abstractmethod
    async def create_role(self, data: dict) -> schemas.RolePermissionSchema: ...

    @abc.abstractmethod
    async def create_default_roles_for_tenant(self, tenant_id: UUID) -> None: ...

    @abc.abstractmethod
    async def update_role(self, data: dict) -> schemas.RolePermissionSchema: ...

    @abc.abstractmethod
    async def delete_role(self, role_id: UUID) -> None: ...


class RolePermissionService(AbstractRolePermissionService):


    def __init__(self, uow: UnitOfWork, current_user: CurrentUser):
        self._uow = uow
        self._current_user = current_user

    async def retrieve_role(self, role_id: UUID) -> tuple[role_permission_domain.Role, list[role_permission_domain.Permission]]:

        role = await self._uow.role_permission_repository.get_role_by_id(role_id=role_id, tenant_id=self._current_user.tenant_id)
        if not role:
            raise NotFoundException(f"Role with id {role_id} not found")

        permission_filters = {
            "role_id": role_id
        }
        permissions = await self._uow.role_permission_repository.list_permission(permission_filters=permission_filters)
        return self._to_role_permission_schema(role=role, permissions=permissions)
        

    async def list_role(self, role_filters: dict, page: int, page_size: int)  -> Pagination:

        role_filters["tenant_id"] = self._current_user.tenant_id
        offset = (page - 1) * page_size
        roles = await self._uow.role_permission_repository.list_role(role_filters, offset, page_size)
        total = await self._uow.role_permission_repository.count_roles(role_filters)
        return Pagination(
            page=page,
            page_size=page_size,
            total=total,
            data=[schemas.Role.model_validate(role) for role in roles]
        )

    async def list_role_option(self, page: int, page_size: int, tenant_id: UUID)  -> schemas.ListRoleOptionSchema:

        role_filters = {"tenant_id": tenant_id}
        offset = (page - 1) * page_size
        roles = await self._uow.role_permission_repository.list_role(role_filters, offset, page_size)
        return schemas.ListRoleOptionSchema(roles=[schemas.RoleOption.model_validate(role) for role in roles])


    async def list_permission(self, permission_filters: dict) -> schemas.ListPermissionSchema:
        
        if not permission_filters.get("role_id"):
            permission_filters["is_staff"] = self._current_user.is_staff

        permissions = await self._uow.role_permission_repository.list_permission(permission_filters)
        return schemas.ListPermissionSchema(
            permissions = [
                schemas.Permission.model_validate(permission) for permission in permissions
            ]
        )

    async def create_role(self, data: dict) -> schemas.RolePermissionSchema:

        role = role_permission_domain.Role.create(
            name = data.get("name"),
            permission_ids=data.get("permission_ids", []),
            created_by_id=self._current_user.id,
            tenant_id=self._current_user.tenant_id,
            is_system_role= False
        )

        if await self._uow.role_permission_repository.role_exists_in_tenant(role.name, role.tenant_id):
            raise AlreadyExistsException(f"Role {role.name} already exists")

        role = await self._uow.role_permission_repository.create_role(role)
        permissions = await self._uow.role_permission_repository.list_permission(permission_filters={"role_id": role.id})

        return self._to_role_permission_schema(role=role, permissions=permissions)


    async def create_default_roles_for_tenant(self, tenant_id: UUID) -> None:
        
        permissions = await self._uow.role_permission_repository.list_permission(permission_filters={"is_staff": False})
        permission_mapping = {
            permission.codename: permission.id
            for permission in permissions
        }
        roles = [
            role_permission_domain.Role.create_default(
                name=default_role["name"],
                tenant_id=tenant_id,
                permission_ids=[permission_mapping.get(code) for code in default_role["permissions"]]
            )
            for default_role in TENANT_DEFAULT_ROLES
        ]
        await self._uow.role_permission_repository.bulk_create_role(roles)


    async def update_role(self, data: dict) -> schemas.RolePermissionSchema:

        role = role_permission_domain.Role.update(
            role_id = data.get("id"),
            name = data.get("name"),
            permission_ids=data.get("permission_ids", []),
            updated_by_id=self._current_user.id,
            tenant_id=self._current_user.tenant_id
        )

        if await self._uow.role_permission_repository.role_exists_in_tenant(role.name, role.tenant_id, role.id):
            raise AlreadyExistsException(f"Role {role.name} already exists")

        role = await self._uow.role_permission_repository.update_role(role)
        permissions = await self._uow.role_permission_repository.list_permission(permission_filters={"role_id": role.id})

        return self._to_role_permission_schema(role=role, permissions=permissions)


    async def delete_role(self, role_id: UUID) -> None:

        role = await self._uow.role_permission_repository.get_role_by_id(role_id, self._current_user.tenant_id)

        if not role:
            raise NotFoundException(f"Role with id {role_id} not found")

        if role.is_system_role:
            raise ForbiddenException("System generated role cannot be deleted")

        if await self._uow.user_repository.role_already_assigned_to_user(role_id):
            raise ResourceInUseError("Cannot delete this role, it has been assigned to user")

        await self._uow.role_permission_repository.delete_role(role_id)


    def _to_role_permission_schema(self, role: role_permission_domain.Role, permissions: role_permission_domain.Permission) -> schemas.RolePermissionSchema:

        return schemas.RolePermissionSchema(
            id = role.id,
            name = role.name,
            is_system_role = role.is_system_role,
            permissions = [
                schemas.Permission(
                    id = permission.id,
                    codename = permission.codename,
                    name = permission.name,
                    description = permission.description
                ) for permission in permissions
            ]
        )