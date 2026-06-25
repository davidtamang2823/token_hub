from fastapi import Depends
from core.unit_of_work import UnitOfWork
from core.context import CurrentUser
from core.dependencies import get_unit_of_work, get_current_user
from tenants.application.services import TenantService
from accounts.role_permission.application.services import RolePermissionService

def get_tenant_service(
    uow: UnitOfWork = Depends(get_unit_of_work), 
    current_user: CurrentUser = Depends(get_current_user)
) -> TenantService:

    return TenantService(
        uow=uow,
        current_user=current_user,
        role_perm_service=RolePermissionService(
            uow=uow, 
            current_user=current_user
        )
    )


