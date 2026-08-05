import abc

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from accounts.auth.domain import models as auth_domain
from accounts.user.infrastructure import orm as user_orm


class AbstractUserAuthRpository(abc.ABC):


    @abc.abstractmethod
    async def get_user_auth_by_email(self, email: str) -> auth_domain.UserAuthModel | None:
        ...

    @abc.abstractmethod
    async def get_user_auth_by_verification_token(self, verification_token: str) -> auth_domain.UserAuthModel | None:
        ...


class UserAuthRepository(AbstractUserAuthRpository):


    def __init__(self, session: AsyncSession):
        self._session = session


    async def get_user_auth_by_email(self, email: str) -> auth_domain.UserAuthModel | None:

        stmt = (
            select(
                user_orm.UserORM.id, 
                user_orm.UserORM.password, 
                user_orm.UserORM.is_active, 
                user_orm.UserORM.is_staff,
                user_orm.UserORM.verified_at
            ).where(user_orm.UserORM.email == email)
        )
        result = await self._session.execute(stmt)
        user_orm_obj = result.one_or_none()
        return self._to_user_auth_domain(user_orm_obj)

    async def get_user_auth_by_verification_token(self, verification_token: str) -> auth_domain.UserAuthModel | None:
        ...


    def _to_user_auth_domain(self, user_orm_obj: user_orm.UserORM) -> auth_domain.UserAuthModel | None:
        if not user_orm_obj:
            return None

        return auth_domain.UserAuthModel(
            id=user_orm_obj.id,
            hashed_password=user_orm_obj.password,
            is_active=user_orm_obj.is_active,
            is_staff=user_orm_obj.is_staff,
            verified_at=user_orm_obj.verified_at
        )





