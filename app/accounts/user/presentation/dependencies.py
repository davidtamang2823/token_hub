from typing import Annotated
from fastapi import Depends
from accounts.user.application.services import AbstractUserService, UserService
from core.dependencies import get_current_user, get_unit_of_work
from core.unit_of_work import UnitOfWork
from core.context import CurrentUser
from core.security import PasswordHandler
from accounts.role_permission.application.policies import TenantAccessPolicy

def get_user_service(uow: Annotated[UnitOfWork, Depends(get_unit_of_work)], current_user: Annotated[CurrentUser, Depends(get_current_user)] ) -> AbstractUserService:
    return UserService(
        uow=uow,
        tenant_access_policy=TenantAccessPolicy(uow=uow, current_user=current_user),
        current_user=current_user,
        password_handler=PasswordHandler()
    )