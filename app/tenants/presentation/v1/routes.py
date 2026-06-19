from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from tenants.presentation.dependencies import get_tenant_service
from tenants.presentation.schemas import TenantSchema
from core.dependencies import require_permission
from core.pagination import Pagination, DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from core.constants.permissions import (
    CAN_ADD_TENANT,
    CAN_UPDATE_TENANT,
    CAN_DELETE_TENANT
)
from tenants.application.services import AbstractTenantService

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants (USER)"]
)

admin_router = APIRouter(
    prefix="/admin/tenants",
    tags=["Tenants (STAFF)"]
)

@admin_router.get("/{tenant_id}", response_model= TenantSchema)
@router.get("/{tenant_id}", response_model= TenantSchema)
async def retrieve_tenant(request: Request, tenant_id: UUID, tenant_service: Annotated [AbstractTenantService, Depends(get_tenant_service)]):

    tenant = await tenant_service.retrieve_tenant(tenant_id=tenant_id)
    return tenant


@admin_router.get("/", response_model = Pagination[TenantSchema])
@router.get("/", response_model = Pagination[TenantSchema])
async def list_tenant(
    request: Request, 
    tenant_service: Annotated [AbstractTenantService, Depends(get_tenant_service)],
    page: int = DEFAULT_PAGE, 
    page_size: int = DEFAULT_PAGE_SIZE,
    is_active: bool | None = None,
    q: str | None = None,

):
    tenant_filters = {
        "is_active": is_active,
        "q": q
    }

    pagination_obj = await tenant_service.list_tenant(
        tenant_filters=tenant_filters,
        page=page,
        page_size=page_size
    )

    return pagination_obj


@admin_router.post(
    "/",
    response_model = TenantSchema, 
    status_code = status.HTTP_201_CREATED,
    dependencies = [Depends(require_permission(CAN_ADD_TENANT))]
)
async def create_tenant(
    request: Request,
    tenant_service: Annotated [AbstractTenantService, Depends(get_tenant_service)]
):
    request_data = await request.json()
    tenant = await tenant_service.create_tenant(data=request_data)
    return tenant


@admin_router.put(
    "/{tenant_id}",
    response_model = TenantSchema,
    dependencies = [Depends(require_permission(CAN_UPDATE_TENANT))]
)
async def update_tenant(
    request: Request,
    tenant_id: UUID,
    tenant_service: Annotated [AbstractTenantService, Depends(get_tenant_service)]
):
    request_data = await request.json()
    request_data["id"] = tenant_id
    tenant = await tenant_service.update_tenant(data=request_data)
    return tenant


@admin_router.delete(
    "/{tenant_id}",
    dependencies = [Depends(require_permission(CAN_DELETE_TENANT))]
)
async def delete_tenant(
    request: Request,
    tenant_id: UUID,
    tenant_service: Annotated [AbstractTenantService, Depends(get_tenant_service)]
):
    await tenant_service.delete_tenant(tenant_id=tenant_id)
    return {"message": "Tenant has been deleted"}