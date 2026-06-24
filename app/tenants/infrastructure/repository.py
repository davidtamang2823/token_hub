import abc
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_, exists
from sqlalchemy.orm import selectinload

from tenants.domain import models as tenant_domain_models
from tenants.infrastructure import orm as tenant_orm
from accounts.user.infrastructure import orm as user_orm


class AbstractTenantRepository(abc.ABC):


    @abc.abstractmethod
    async def get_tenant_by_id(self, tenant_id: UUID) -> tenant_domain_models.Tenant | None: ...

    @abc.abstractmethod
    async def get_tenant_by_name(self, name: str, exclude_tenant_id: UUID = None) -> tenant_domain_models.Tenant | None: ...

    @abc.abstractmethod
    async def tenant_id_exists(self, tenant_id: UUID) -> bool: ...

    @abc.abstractmethod
    async def tenant_name_exists(self, name: str, exclude_tenant_id: UUID = None) -> bool: ...

    @abc.abstractmethod
    async def tenant_code_exists(self, code: str, exclude_tenant_id: UUID = None) -> bool: ...

    @abc.abstractmethod
    async def get_tenant_by_code(self, code: str, exclude_tenant_id: UUID = None) -> tenant_domain_models.Tenant | None: ...

    @abc.abstractmethod
    async def list_tenant(self, tenant_filters: dict, limit: int, offset: int) -> tuple[list[tenant_domain_models.Tenant], int]: ...

    @abc.abstractmethod
    async def create_tenant(self, tenant: tenant_domain_models.Tenant) -> tenant_domain_models.Tenant: ...

    @abc.abstractmethod
    async def update_tenant(self, tenant: tenant_domain_models.Tenant) -> tenant_domain_models.Tenant: ...

    @abc.abstractmethod
    async def delete_tenant(self, tenant_id: UUID) -> None: ...


class TenantRepository(AbstractTenantRepository):


    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_tenant_by_id(self, tenant_id: UUID) -> tenant_domain_models.Tenant:
        
        stmt = (
            select(tenant_orm.Tenant)
            .where(
                tenant_orm.Tenant.id == tenant_id, 
                tenant_orm.Tenant.is_deleted == False
            )
        )
        result = await self._session.execute(stmt)
        tenant_orm_obj = result.scalar_one_or_none()
        return self._to_tenant_domain_model(
            tenant_orm_obj=tenant_orm_obj
        ) 

    async def get_tenant_by_name(self, name: str, exclude_tenant_id: UUID | None = None) -> tenant_domain_models.Tenant | None:
        
        stmt = (
            select(tenant_orm.Tenant)
            .where(
                tenant_orm.Tenant.name.ilike(name), 
                tenant_orm.Tenant.is_deleted == False
            )
        )
        if exclude_tenant_id:
            stmt = stmt.where(tenant_orm.Tenant.id != exclude_tenant_id)

        result = await self._session.execute(stmt)
        tenant_orm_obj = result.scalar_one_or_none()
        return self._to_tenant_domain_model(
            tenant_orm_obj=tenant_orm_obj
        ) 

    async def get_tenant_by_code(self, code: str, exclude_tenant_id: UUID | None = None) -> tenant_domain_models.Tenant | None:
        
        stmt = (
            select(tenant_orm.Tenant)
            .where(
                tenant_orm.Tenant.code.ilike(code), 
                tenant_orm.Tenant.is_deleted == False
            )
        )
        if exclude_tenant_id:
            stmt = stmt.where(tenant_orm.Tenant.id != exclude_tenant_id)

        result = await self._session.execute(stmt)
        tenant_orm_obj = result.scalar_one_or_none()
        return self._to_tenant_domain_model(
            tenant_orm_obj=tenant_orm_obj
        ) 


    async def tenant_id_exists(self, tenant_id: UUID) -> bool:

        stmt = (
            select(
                exists()
                .where(tenant_orm.Tenant.id == tenant_id)
            )
        )

        result = await self._session.execute(stmt)
        return result.scalar()


    async def tenant_name_exists(self, name: str, exclude_tenant_id: UUID = None) -> bool:

        exists_stmt = (
            exists()
            .where(tenant_orm.Tenant.name.ilike(name), tenant_orm.Tenant.is_deleted==False)
        )
        if exclude_tenant_id:
            exists_stmt = exists_stmt.where(tenant_orm.Tenant.id != exclude_tenant_id)
        stmt = (
            select(
               exists_stmt
            )
        )

        result = await self._session.execute(stmt)
        return result.scalar()

    async def tenant_code_exists(self, code: str, exclude_tenant_id: UUID = None) -> bool:

        exists_stmt = (
            exists()
            .where(tenant_orm.Tenant.code.ilike(code), tenant_orm.Tenant.is_deleted==False)
        )
        
        if exclude_tenant_id:
            exists_stmt = exists_stmt.where(tenant_orm.Tenant.id != exclude_tenant_id)
        
        stmt = (
            select(
                exists_stmt
            )
        )

        result = await self._session.execute(stmt)
        return result.scalar()



    async def list_tenant(self, tenant_filters: dict, limit: int, offset: int) -> tuple[list[tenant_domain_models.Tenant], int]:
        
        has_view_all_tenant_permission = tenant_filters.get("has_view_all_tenant_permission", False)
        user_id = tenant_filters.get("user_id")
        search_key = tenant_filters.get("q")
        is_active = tenant_filters.get("is_active")

        if has_view_all_tenant_permission:
            stmt = (
                select(tenant_orm.Tenant)
                .where(tenant_orm.Tenant.is_deleted == False)
                
            )
        else:
            stmt = (
                select(tenant_orm.Tenant)
                .join(user_orm.UserTenant, tenant_orm.Tenant.id==user_orm.UserTenant.tenant_id)
                .where(user_orm.UserTenant.user_id == user_id, tenant_orm.Tenant.is_deleted == False)
            )

        if search_key:
            stmt = (
                stmt
                .where(
                    or_(
                        tenant_orm.Tenant.name.ilike(f"{search_key}%"), 
                        tenant_orm.Tenant.code.ilike(f"{search_key}%")
                    )
                )
            
            )

        if is_active is not None:
            stmt = (
                stmt
                .where(
                    tenant_orm.Tenant.is_active == is_active
                )
            )
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self._session.scalar(count_stmt)
        stmt = stmt.distinct().order_by(tenant_orm.Tenant.name).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        user_orm_objs = result.scalars().all()
        tenants = [self._to_tenant_domain_model(user_orm_obj) for user_orm_obj in user_orm_objs]
        return tenants, total


    async def create_tenant(self, tenant: tenant_domain_models.Tenant) -> tenant_domain_models.Tenant:
        
        tenant_orm_obj = tenant_orm.Tenant(
            id = tenant.id,
            name = tenant.name,
            code = tenant.code,
            is_active = tenant.is_active,
            created_by_id=tenant.created_by_id
        )
        self._session.add(tenant_orm_obj)
        return tenant

    async def update_tenant(self, tenant: tenant_domain_models.Tenant) -> tenant_domain_models.Tenant:
        
        stmt = (
            update(tenant_orm.Tenant)
            .where(tenant_orm.Tenant.id == tenant.id)
            .values(
                name = tenant.name,
                code = tenant.code,
                is_active = tenant.is_active,
                updated_by_id=tenant.updated_by_id
            )
        )
        await self._session.execute(stmt)
        return tenant


    async def delete_tenant(self, tenant_id: UUID) -> None:
        
        stmt = (
            update(tenant_orm.Tenant)
            .where(tenant_orm.Tenant.id == tenant_id)
            .values(
                is_deleted = True
            )
        )
        await self._session.execute(stmt)

    def _to_tenant_domain_model(self, tenant_orm_obj: tenant_orm.Tenant) -> tenant_domain_models.Tenant | None:

        if tenant_orm_obj:
            return tenant_domain_models.Tenant(
                id = tenant_orm_obj.id,
                name = tenant_orm_obj.name,
                code = tenant_orm_obj.code,
                is_active = tenant_orm_obj.is_active,
            )