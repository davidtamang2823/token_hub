from sqlalchemy.ext.asyncio import AsyncSession
from accounts.user.infrastructure.repository import UserRepository
from accounts.auth.infrastructure.repository import UserAuthRepository
from tenants.infrastructure.repository import TenantRepository

class UnitOfWork:

    def __init__(self, session: AsyncSession):
        self._session = session
    

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, exc_traceback):

        if not exc_type:
            await self._session.commit()
        else:
            await self._session.rollback()

    @property
    def user_repository(self):
        return UserRepository(self._session)

    @property
    def user_auth_repository(self):
        return UserAuthRepository(self._session)

    @property
    def tenant_repository(self):
        return TenantRepository(self._session)