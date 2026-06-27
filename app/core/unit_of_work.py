from sqlalchemy.ext.asyncio import AsyncSession
from accounts.user.infrastructure.repository import AbstractUserRepository, UserRepository
from accounts.auth.infrastructure.repository import AbstractUserAuthRpository, UserAuthRepository
from tenants.infrastructure.repository import AbstractTenantRepository, TenantRepository
from accounts.role_permission.infrastructure.repository import AbstractRolePermissionRepository, RolePermissionRepository
from core.events import EventBus
from core.domain import AggregateRoot

class UnitOfWork:

    def __init__(self, session: AsyncSession, event_bus: EventBus):
        self._session = session
        self._event_bus = event_bus
        self._tracked_entities: list[AggregateRoot] = []
    
    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_value, exc_traceback) -> None:

        if not exc_type:
            await self._session.commit()
            self._publish_events()
        else:
            await self._session.rollback()

    def register_entity(self, entity: AggregateRoot) -> None:
        self._tracked_entities.add(entity)

    def _publish_events(self) -> None:

        for tracked_entity in self._tracked_entities:
            events = tracked_entity.pull_events()
            self._event_bus.publish(events)

        self._tracked_entities = []

    @property
    def user_repository(self) -> AbstractUserRepository:
        return UserRepository(self._session)

    @property
    def user_auth_repository(self) -> AbstractUserAuthRpository:
        return UserAuthRepository(self._session)

    @property
    def tenant_repository(self) -> AbstractTenantRepository:
        return TenantRepository(self._session)

    @property
    def role_permission_repository(self) -> AbstractRolePermissionRepository:
        return RolePermissionRepository(self._session)