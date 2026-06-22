from fastapi import Depends
from core.unit_of_work import UnitOfWork
from core.context import CurrentUser
from core.dependencies import get_unit_of_work, get_current_user
from accounts.role_permission.application.services import RolePermissionService

def get_role_permission_service(
    uow: UnitOfWork = Depends(get_unit_of_work), 
    current_user: CurrentUser = Depends(get_current_user)
):
    return RolePermissionService(
        uow=uow,
        current_user=current_user
    )