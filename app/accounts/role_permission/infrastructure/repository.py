import abc
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, exists
from sqlalchemy.orm import selectinload
from accounts.role_permission.infrastructure import orm as  role_permission_orm
from accounts.role_permission.domain import models as role_permission_domain


class AbstractRolePermissionRepository(abc.ABC):


    @abc.abstractmethod
    async def get_role_by_id(self, role_id: UUID) -> role_permission_domain.Role: ...

    @abc.abstractmethod
    async def get_role_by_name_and_tenant_id(self, name: str, tenant_id: UUID | None = None) -> role_permission_domain.Role: ...

    @abc.abstractmethod
    async def list_role(self, role_filters: dict, offset: int, limit: int)  -> tuple[int, list[role_permission_orm.Role]]: ...

    @abc.abstractmethod
    async def list_permission(self, permission_filters: dict) -> list[role_permission_domain.Permission]: ...

    @abc.abstractmethod
    async def create_role(self, role: role_permission_domain.Role) -> role_permission_domain.Role: ...

    @abc.abstractmethod
    async def update_role(self, role: role_permission_domain.Role) -> role_permission_domain.Role: ...

    @abc.abstractmethod
    async def delete_role(self, role_id: UUID) -> None: ...


class RolePermissionRepository(AbstractRolePermissionRepository):


    def __init__(self, session: AsyncSession):
        self._session = session


    async def get_role_by_id(self, role_id: UUID) -> role_permission_domain.Role | None:
        
        stmt = (
            select(
                role_permission_orm.Role
            )
            .options(
                selectinload(
                    role_permission_orm.Role.permissions
                )
            )
            .where(role_permission_orm.Role.id == role_id)
        )

        result = await self._session.execute(stmt)
        
        return self._to_role_domain_model(result.scalar_one_or_none())

    async def get_role_by_name_and_tenant_id(self, name: str, tenant_id: UUID | None = None) -> role_permission_domain.Role | None:
        
        stmt = (
            select(
                role_permission_orm.Role
            )
            .options(
                selectinload(
                    role_permission_orm.Role.permissions
                )
            )
            .where(
                role_permission_orm.Role.name.ilike(name), 
                role_permission_orm.Role.tenant_id == tenant_id
            )
        )

        result = await self._session.execute(stmt)
        
        return self._to_role_domain_model(result.scalar_one_or_none())

    async def list_role(self, role_filters: dict, offset: int, limit: int)  -> tuple[int, list[role_permission_orm.Role]]:
        
        tenant_id = role_filters.get("tenant_id")
        search_key = role_filters.get("q")

        stmt = (
            select(role_permission_orm.Role)
            .where(role_permission_orm.Role.tenant_id == tenant_id)
        )

        if search_key:
            stmt = stmt.where(role_permission_orm.Role.name.ilike(f"{search_key}%"))
        

        total = (
            await self._session.scalar(
                select(
                    func.count()
                )
                .select_from(
                    stmt.subquery()
                )
            )
        )

        result = await self._session.execute(
            stmt.order_by(
                role_permission_orm.Role.name
            )
            .offset(offset)
            .limit(limit)
        )

        roles = list(result.scalars().all())
        
        return total, roles



    async def list_permission(self, permission_filters: dict) -> list[role_permission_domain.Permission]:


        is_staff = permission_filters.get("is_staff")
        search_key = permission_filters.get("q")
        role_id = permission_filters.get("role_id")

        if role_id:
            stmt = (
                select(
                    role_permission_orm.Permission
                )
                .join(
                    role_permission_orm.RolePermission, 
                    role_permission_orm.RolePermission.permission_id == role_permission_orm.Permission.id
                )
                .where(role_permission_orm.RolePermission.role_id == role_id)
            )
        else:
            stmt = (
                select(
                    role_permission_orm.Permission
                )
            )

        if search_key:
            stmt = stmt.where(role_permission_orm.Permission.name.ilike(f"{search_key}%"))

        if is_staff is not None:
            stmt = stmt.where(role_permission_orm.Permission.is_super_admin_permission == is_staff)
        
        result = await self._session.execute(
            stmt.order_by(role_permission_orm.Permission.name).distinct()
        )

        permissions = [self._to_permission_domain_model(permission_orm_obj) for permission_orm_obj in result.scalars().all()]

        return permissions


    async def create_role(self, role: role_permission_domain.Role) -> role_permission_domain.Role:

        role_orm_obj = role_permission_orm.Role(
            id = role.id,
            name = role.name,
            created_by_id = role.created_by_id,
            tenant_id = role.tenant_id,
            is_system_role = False
        )

        permission_stmt = (
            select(
                role_permission_orm.Permission
            )
            .where(
                role_permission_orm.Permission.id.in_(role.permission_ids)
            )
        )

        permission_result = await self._session.execute(permission_stmt)
        permission_orm_objs = list(permission_result.scalars.all())
        role_orm_obj.permissions = permission_orm_objs

        self._session.add(role_orm_obj)
        await self._session.flush()

        return self._to_role_domain_model(role_orm_obj=role_orm_obj)



    async def update_role(self, role: role_permission_domain.Role) -> role_permission_domain.Role | None:

        role_stmt = (
            select(role_permission_orm.Role)
            .where(role_permission_orm.Role.id == role.id)
        )

        role_result = await self._session.execute(role_stmt)
        role_orm_obj = role_result.scalar_one_or_none()
        
        if not role_orm_obj:
            return None

        permission_stmt = (
            select(
                role_permission_orm.Permission
            )
            .where(
                role_permission_orm.Permission.id.in_(role.permission_ids)
            )
        )

        permission_result = await self._session.execute(permission_stmt)
        permission_orm_objs = list(permission_result.scalars.all())

        role_orm_obj.name = role.name
        role_orm_obj.updated_by_id = role.updated_by_id
        role_orm_obj.permissions = permission_orm_objs

        await self._session.flush()

        return self._to_role_domain_model(role_orm_obj)


    async def delete_role(self, role_id: UUID) -> None:

        stmt = (
            delete(role_permission_orm.Role)
            .where(role_permission_orm.Role.id == role_id)
        )

        await self._session.execute(stmt)

    def _to_role_domain_model(self, role_orm_obj: role_permission_orm.Role) -> role_permission_domain.Role | None:

        if role_orm_obj:
            return role_permission_domain.Role(
                id = role_orm_obj.id,
                name = role_orm_obj.name,
                tenant_id = role_orm_obj.tenant_id,
                is_system_role = role_orm_obj.is_system_role,
                permission_ids = [permission.id for permission in role_orm_obj.permissions]
            ) 

    def _to_permission_domain_model(self, permission_orm_obj: role_permission_orm.Permission) -> role_permission_domain.Permission | None:

        if permission_orm_obj:

            return role_permission_domain.Permission(
                id =  permission_orm_obj.id,
                name = permission_orm_obj.name,
                codename = permission_orm_obj.codename,
                description = permission_orm_obj.description
            )