from typing import Annotated
from fastapi import Depends
from accounts.user.application.services import AbstractUserService, UserService
from core.dependencies import get_current_user, get_unit_of_work, get_tenant_access_policy
from core.unit_of_work import UnitOfWork

def get_user_service(uow: Annotated[UnitOfWork, Depends(get_unit_of_work)]) -> AbstractUserService:
    return UserService(
        uow=uow,
        tenant_access_policy=get_tenant_access_policy(),
        current_user=get_current_user()
    )