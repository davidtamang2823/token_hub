import abc
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
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
    
    @abc.abstractmethod
    async def get_user_verification_by_token(self, verification_token: str) -> auth_domain.UserVerificationModel | None: ...

    @abc.abstractmethod
    async def get_user_verification_by_email(self, email: str) -> auth_domain.UserVerificationModel | None: ...

    @abc.abstractmethod
    async def get_user_password_reset_request_by_email(self, email: str) -> auth_domain.UserPasswordResetModel | None: ...

    @abc.abstractmethod
    async def save_user_verification(self, user_id: str, hashed_password: str, verified_at: datetime) -> None: ...

    @abc.abstractmethod
    async def update_user_verification(self, verify: auth_domain.UserVerificationModel) -> None: ...

    @abc.abstractmethod
    async def save_user_new_password_verification(self, password_reset: auth_domain.UserPasswordResetModel) -> None: ...

    @abc.abstractmethod
    async def update_password(self, user_id: UUID, hashed_password: str) ->  None: ...

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


    async def get_user_verification_by_token(self, verification_token: str) -> auth_domain.UserVerificationModel | None:
        stmt = (
            select(user_orm.UserORM)
            .where(user_orm.UserORM.verification_token == verification_token)
        )

        user_orm_obj = (await self._session.execute(stmt)).scalar_one_or_none()
        if user_orm_obj:
            return auth_domain.UserVerificationModel(
                user_id = user_orm_obj.id,
                email = user_orm_obj.email,
                verification_token = user_orm_obj.verification_token,
                verification_token_created_at = user_orm_obj.verification_token_created_at,
                verified_at = user_orm_obj.verified_at
            )


    async def get_user_verification_by_email(self, email: str) -> auth_domain.UserVerificationModel | None:
        stmt = (
            select(user_orm.UserORM)
            .where(user_orm.UserORM.email == email)
        )

        user_orm_obj = (await self._session.execute(stmt)).scalar_one_or_none()
        if user_orm_obj:
            return auth_domain.UserVerificationModel(
                user_id = user_orm_obj.id,
                email = user_orm_obj.email,
                verification_token = user_orm_obj.verification_token,
                verficiation_token_created_at = user_orm_obj.verification_token_created_at,
                verified_at = user_orm_obj.verified_at
            )


    async def get_user_password_reset_request_by_email(self, email: str) -> auth_domain.UserPasswordResetModel | None:

        stmt = (
            select(user_orm.UserORM)
            .where(user_orm.UserORM.email == email)
        )

        user_orm_obj = (await self._session.execute(stmt)).scalar_one_or_none()
        if user_orm_obj:
            return auth_domain.UserPasswordResetModel(
                user_id = user_orm_obj.id,
                email = user_orm_obj.email,
                new_password_verification_token = user_orm_obj.new_password_verification_token,
                new_password_verification_token_created_at = user_orm_obj.new_password_verification_token_created_at
            )

    async def save_user_verification(self, user_id: str, hashed_password: str, verified_at: datetime) -> None:
        stmt = (
            update(user_orm.UserORM)
            .where(user_orm.UserORM.id == user_id)
            .values(
                password = hashed_password,
                verified_at = verified_at,
                is_active = True
            )
        )

        await self._session.execute(stmt)


    async def update_user_verification(self, verify: auth_domain.UserVerificationModel) -> None:

        stmt = (
            update(user_orm.UserORM)
            .where(user_orm.UserORM.id == verification.user_id)
            .values(
                verification_token = verify.verification_token,
                verification_token_created_at = verify.verification_token_created_at
            )
        )

        await self._session.execute(stmt)


    async def save_user_new_password_verification(self, password_reset: auth_domain.UserPasswordResetModel) -> None:

        stmt = (
            update(user_orm.UserORM)
            .where(user_orm.UserORM.email == password_reset.email)
            .values(
                new_password_verification_token = password_reset.new_password_verification_token,
                new_password_verification_token_created_at = password_reset.new_password_verification_token_created_at
            )
        )
        await self._session.execute(stmt)


    async def update_password(self, user_id: UUID, hashed_password: str) ->  None:

        stmt = (
            update(user_orm.UserORM)
            .where(user_orm.UserORM.id == user_id)
            .values(password = hashed_password)
        )

        await self._session.execute(stmt)

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





