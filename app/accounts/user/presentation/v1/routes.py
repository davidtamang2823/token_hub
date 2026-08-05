from fastapi import APIRouter, Depends
from fastapi.requests import Request
from accounts.user.presentation.dependencies import get_user_service
from accounts.user.application.services import AbstractUserService
from core.dependencies import require_permission
from core.constants.permissions import CAN_VIEW_USER, CAN_UPDATE_USER, CAN_DELETE_USER, CAN_ADD_USER_TO_TENANT, CAN_REMOVE_USER_FROM_TENANT
from core.pagination import Pagination, DEFAULT_PAGE, DEFAULT_PAGE_SIZE

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

admin_router = APIRouter(
    prefix="/admin/users",
    tags=["Users (Admin)"]
)


@router.get("", dependencies=[Depends(require_permission(CAN_VIEW_USER))])
async def list_user(request: Request, user_service: AbstractUserService = Depends(get_user_service)):
    ...