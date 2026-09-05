from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from accounts.user.presentation.dependencies import get_user_service
from accounts.user.application.services import AbstractUserService
from core.dependencies import require_permission, get_current_user, verify_tenant_membership
from core.constants.permissions import (
    CAN_VIEW_USER, 
    CAN_CREATE_USER, 
    CAN_UPDATE_USER, 
    CAN_DELETE_USER, 
    CAN_ADD_USER_TO_TENANT, 
    CAN_REMOVE_USER_FROM_TENANT,
    CAN_UPDATE_USER_EMAIL
)
from core.pagination import Pagination, DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from core.context import CurrentUser
from accounts.user.application import dtos

public_router = APIRouter(
    prefix="/users",
    tags=["Public User Routes"]
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

admin_router = APIRouter(
    prefix="/admin/users",
    tags=["Users (Admin)"]
)


@router.get("", dependencies=[Depends(require_permission([CAN_VIEW_USER]))], response_model=Pagination)
@admin_router.get("", dependencies=[Depends(require_permission([CAN_VIEW_USER]))], response_model=Pagination)
async def list_user(
    request: Request, 
    user_service: Annotated[AbstractUserService, Depends(get_user_service)], 
    tenant_id: UUID | None = None, 
    is_active: bool | None = None, 
    q: str | None = None,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE,
    drop_down: bool = False
):

    user_filters = {
        "tenant_id": tenant_id,
        "is_active": is_active,
        "q": q,
        "drop_down": drop_down,
    }

    paginated_response = await user_service.list_user(user_filters=user_filters, page=page, page_size=page_size)
    return paginated_response


@admin_router.get("/{me}")
async def retrive_user(
    request: Request, 
    user_service: Annotated[AbstractUserService, Depends(get_user_service)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
):
    response_data = await user_service.retrive_user(current_user.id)
    return response_data


@router.get("/{user_id}", dependencies=[Depends(require_permission([CAN_VIEW_USER]))])
@admin_router.get("/{user_id}", dependencies=[Depends(require_permission([CAN_VIEW_USER]))])
async def retrieve_user(request: Request, user_id: UUID, user_service: Annotated[AbstractUserService, Depends(get_user_service)]):

    response_data = await user_service.retrive_user(user_id=user_id)
    return response_data

@router.post("", dependencies=[Depends(require_permission([CAN_ADD_USER_TO_TENANT]))])
@admin_router.post("", dependencies=[Depends(require_permission([CAN_ADD_USER_TO_TENANT]))])
async def add_user_to_tenant(request: Request, user_service: Annotated[AbstractUserService, Depends(get_user_service)]):

    request_data = await request.json()
    await user_service.add_user_to_tenant(data = request_data)
    return {"message": "User added to tenant successfully"}

@admin_router.post("", dependencies=[Depends(require_permission([CAN_CREATE_USER]))])
async def create_user(request: Request, user_service: Annotated[AbstractUserService, Depends(get_user_service)]):
    request_data = await request.json()
    await user_service.create_user(data=request_data)
    return {"message": "User created successfully"}

@router.post("/request-email-change")
@admin_router.post("/request-email-change")
async def request_user_email_change(request: Request, request_email_change: dtos.RequestUserEmailChangeDTO, user_service: Annotated[AbstractUserService, Depends(get_user_service)]):

    await user_service.request_user_email_change(email_change=request_email_change)
    return {"message": "User email change request has been sent"}

@router.put("/approve-email-change-request", dependencies=[Depends(require_permission([CAN_UPDATE_USER_EMAIL]))])
@router.put("/reject-email-change-request", dependencies=[Depends(require_permission([CAN_UPDATE_USER_EMAIL]))])
@admin_router.put("/approve-email-change-request", dependencies=[Depends(require_permission([CAN_UPDATE_USER_EMAIL]))])
@admin_router.put("/reject-email-change-request", dependencies=[Depends(require_permission([CAN_UPDATE_USER_EMAIL]))])
async def handle_user_email_change_request(
    request: Request, 
    handle_request: dtos.HandleUserEmailChangeRequestDTO,
    user_service: Annotated[AbstractUserService, Depends(get_user_service)]
):

    await user_service.handle_user_email_change_request(handle_request)
    return {
        "message": "Email change request has been Approved" if handle_request.is_approved
        else "Email change request has been Rejected"   
    }

@public_router.put("/update-email")
async def update_email(
    request: Request, 
    update_email: dtos.UpdateEmailDTO, 
    user_service: Annotated[AbstractUserService, Depends(get_user_service)]
):

    await user_service.update_user_email(new_email_verification_token=update_email.new_email_verification_token)
    return {
        "message": "User email has been updated, please login with new email"
    }

@router.put("/update-name/{user_id}", dependencies=[Depends(require_permission([CAN_UPDATE_USER]))])
@admin_router.put("/update-name/{user_id}", dependencies=[Depends(require_permission([CAN_UPDATE_USER]))])
async def update_user_name(
    request: Request,
    update_user_name: dtos.UpdateUserNameDTO,
    user_service: Annotated[AbstractUserService, Depends(get_user_service)],
    user_id: UUID | None = None
):
    reponse_data = await user_service.update_user_name(user_dto=update_user_name, user_id=user_id)
    return reponse_data


@admin_router.put("/update-status", dependencies=[Depends(require_permission([CAN_UPDATE_USER]))])
async def update_user_status(
    request: Request,
    update_user_status: dtos.UpdateUserStatusDTO,
    user_service: Annotated[AbstractUserService, Depends(get_user_service)],
):
    await user_service.update_user_status(update_user_status)
    return {
        "message": "User status has been updated"
    }

@router.put("/update-role", dependencies=[Depends(require_permission([CAN_UPDATE_USER]))])
@admin_router.put("/update-role", dependencies=[Depends(require_permission([CAN_UPDATE_USER]))])
async def update_user_role(
    request: Request,
    update_user_role: dtos.UpdateRoleDTO,
    user_service: Annotated[AbstractUserService, Depends(get_user_service)],
):
    await user_service.update_user_role(update_user_role)
    return {"message": "User role has been updated"}

@router.delete("/delete-user-tenant/{user_id}", dependencies=[Depends(require_permission([CAN_REMOVE_USER_FROM_TENANT]))])
@admin_router.delete("/delete-user-tenant/{user_id}/{tenant_id}", dependencies=[Depends(require_permission([CAN_REMOVE_USER_FROM_TENANT]))])
async def remove_user_from_tenant(
    request: Request, 
    user_id: UUID, 
    user_service: Annotated[AbstractUserService, Depends(get_user_service)],
    tenant_id: UUID | None = None
):
    await user_service.remove_user_from_tenant(user_id=user_id, tenant_id=tenant_id)
    return {
        "message": "User removed from tenant"
    }

@admin_router.delete("/delete-user/{user_id}", dependencies=[Depends(require_permission([CAN_DELETE_USER]))])
async def delete_user(
    request: Request, 
    user_id: UUID, 
    user_service: Annotated[AbstractUserService, Depends(get_user_service)],
):
    await user_service.delete_user(user_id=user_id)
    return{
        "message": "User has been deleted"
    }