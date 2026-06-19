from uuid import UUID
from typing import Callable
from fastapi import Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db_session
from core.unit_of_work import UnitOfWork
from core.context import CurrentUser
from core.exceptions import ForbiddenException, NotFoundException


async def get_unit_of_work(session:AsyncSession = Depends(get_db_session)) -> UnitOfWork:

    async with UnitOfWork(session) as uow:
        yield uow


def get_current_user(request:Request) -> CurrentUser:
    return request.state.current_user


def require_permission(permissions: list[str], action: str | None = None) -> Callable:

    def dependency(request: Request):

        user_permissions = request.state.current_user.permissions
        if not any(user_permission in permissions for user_permission in user_permissions):
            message = (
                f"You do not have permission to perform {action} action"
                if action
                else "You do not have permission to perform this action"
            )
            raise ForbiddenException(message)

    return dependency


async def verify_tenant_membership(
    request: Request,
    x_tenant_id: UUID = Header(..., alias="X-Tenant-ID"),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> UUID:

    current_user = request.state.current_user

    is_user_assigned_to_tenant = await uow.user_repository.exists_in_tenant(
        user_id=current_user.id,
        tenant_id=x_tenant_id,
    )
    if not is_user_assigned_to_tenant:
        raise ForbiddenException("User not assigned to this tenant")

    tenant = await uow.tenant_repository.get_tenant_by_id(tenant_id=x_tenant_id)
    if not tenant:
        raise NotFoundException(f"Tenant with id {x_tenant_id} not found")

    if not tenant.is_active:
        raise ForbiddenException(f"Tenant with id {x_tenant_id} not active")

    return x_tenant_id