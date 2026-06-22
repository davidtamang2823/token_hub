from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Request
from core.dependencies import require_permission, get_current_user
from core.context import CurrentUser
from core.pagination import Pagination, DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from core.constants.permissions import (
    CAN_CREATE_ROLE,
    CAN_UPDATE_ROLE,
    CAN_DELETE_ROLE,
    CAN_VIEW_ROLE,
    CAN_ADD_USER_TO_TENANT
)
from accounts.role_permission.presentation.dependencies import get_role_permission_service
from accounts.role_permission.application.services import AbstractRolePermissionService
from accounts.role_permission.presentation.schemas import RolePermissionSchema, ListPermissionSchema, ListRoleOptionSchema

router = APIRouter(
    prefix="",
    tags=["Roles and Permissions (USER)"]
)

admin_router = APIRouter(
    prefix="/admin",
    tags=["Roles and Permissions (ADMIN)"]
)


@router.get("/roles/me", response_model=RolePermissionSchema)
@admin_router.get("/roles/me", response_model=RolePermissionSchema)
async def retrieve_own_role(
    request: Request,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    role_permission_service: Annotated[AbstractRolePermissionService, Depends(get_role_permission_service)],
):
    return await role_permission_service.retrieve_role(role_id=current_user.role_id)


@router.get("/roles/{role_id}", dependencies=[Depends(require_permission([CAN_VIEW_ROLE, CAN_UPDATE_ROLE]))], response_model=RolePermissionSchema)
@admin_router.get("/roles/{role_id}", dependencies=[Depends(require_permission([CAN_VIEW_ROLE, CAN_UPDATE_ROLE]))], response_model=RolePermissionSchema)
async def retrieve_role(
    request: Request, 
    role_id: UUID, 
    role_permission_service: Annotated[AbstractRolePermissionService, Depends(get_role_permission_service)]
):
    return await role_permission_service.retrieve_role(role_id=role_id)


@router.get("/roles", dependencies=[Depends(require_permission([CAN_VIEW_ROLE]))], response_model=Pagination)
@admin_router.get("/roles", dependencies=[Depends(require_permission([CAN_VIEW_ROLE]))], response_model=Pagination)
async def list_role(
    request: Request,
    role_permission_service: Annotated[AbstractRolePermissionService, Depends(get_role_permission_service)],
    page: int = DEFAULT_PAGE, 
    page_size: int = DEFAULT_PAGE_SIZE, 
    q: str | None = None
):
    role_filters = {
        "q": q
    }

    return await role_permission_service.list_role(role_filters=role_filters, page=page, page_size=page_size)

@admin_router.get("/tenants/{tenant_id}/roles", dependencies=[Depends(require_permission([CAN_ADD_USER_TO_TENANT]))], response_model=ListRoleOptionSchema)
async def list_role_option(
    request: Request,
    tenant_id: UUID,
    role_permission_service: Annotated[AbstractRolePermissionService, Depends(get_role_permission_service)],
    page: int = DEFAULT_PAGE, 
    page_size: int = 100, 
): 

    return await role_permission_service.list_role_option(page=page, page_size=page_size, tenant_id=tenant_id)


@router.get("/permissions", dependencies=[Depends(require_permission([CAN_CREATE_ROLE, CAN_UPDATE_ROLE]))], response_model=ListPermissionSchema)
@admin_router.get("/permissions", dependencies=[Depends(require_permission([CAN_CREATE_ROLE, CAN_UPDATE_ROLE]))], response_model=ListPermissionSchema)
async def list_permission(
    request: Request,
    role_permission_service: Annotated[AbstractRolePermissionService, Depends(get_role_permission_service)],
    q: str | None = None
):
    permission_filters = {"q": q}
    return await role_permission_service.list_permission(permission_filters=permission_filters)

@router.post("/roles", dependencies=[Depends(require_permission([CAN_CREATE_ROLE]))], response_model=RolePermissionSchema)
@admin_router.post("/roles", dependencies=[Depends(require_permission([CAN_CREATE_ROLE]))], response_model=RolePermissionSchema)
async def create_role(
    request: Request,
    role_permission_service: Annotated[AbstractRolePermissionService, Depends(get_role_permission_service)]
):
    request_data = await request.json()
    return await role_permission_service.create_role(data=request_data)


@router.put("/roles/{role_id}", dependencies=[Depends(require_permission([CAN_UPDATE_ROLE]))], response_model=RolePermissionSchema)
@admin_router.put("/roles/{role_id}", dependencies=[Depends(require_permission([CAN_UPDATE_ROLE]))], response_model=RolePermissionSchema)
async def update_role(
    request: Request,
    role_id: UUID,
    role_permission_service: Annotated[AbstractRolePermissionService, Depends(get_role_permission_service)]
):
    request_data = await request.json()
    request_data["id"] = role_id
    return await role_permission_service.update_role(data=request_data)


@router.delete("/roles/{role_id}", dependencies=[Depends(require_permission([CAN_DELETE_ROLE]))])
@admin_router.delete("/roles/{role_id}", dependencies=[Depends(require_permission([CAN_DELETE_ROLE]))])
async def delete_role(
    request: Request,
    role_id: UUID,
    role_permission_service: Annotated[AbstractRolePermissionService, Depends(get_role_permission_service)]
):

    await role_permission_service.delete_role(role_id=role_id)
    return {"message": "Role has been deleted"}