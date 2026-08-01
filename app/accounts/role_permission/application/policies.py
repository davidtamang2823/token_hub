from core.unit_of_work import UnitOfWork
from core.context import CurrentUser
from core.constants.permissions import CAN_VIEW_ALL_TENANT


class TenantAccessPolicy:
    def __init__(self, uow: UnitOfWork, current_user: CurrentUser) -> None:
        self._uow = uow
        self._current_user = current_user

    async def ensure_user_in_tenant(self, tenant_id: UUID) -> None:
        user_exists_in_tenant = (
            CAN_VIEW_ALL_TENANT in self._current_user.permissions
            or await self._uow.user_repository.user_exists_in_tenant(
                user_id=self._current_user.id, tenant_id=tenant_id
            )
        )
        if not user_exists_in_tenant:
            raise ForbiddenException(
                "Cannot perform this operation, current logged in user not assigned to this tenant"
            )