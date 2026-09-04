import abc
import typing
import secrets
from datetime import datetime, timezone
from uuid import UUID
from core.security import AbstractTokenHandler, AbstractPasswordHandler
from core.unit_of_work import UnitOfWork
from core.exceptions import UnauthorizedException, TokenExpiredException, NotFoundException, InvalidStateTransitionException, VerificationCooldownException
from accounts.auth.application import dtos
from accounts.auth.domain import models as auth_domain

class AbstractAuthService(abc.ABC):


    @abc.abstractmethod
    async def login(self, email: str, password: str):
        ...
    
    @abc.abstractmethod
    async def verify_user(self, verify: dtos.VerifyUserDTO):
        ...

    @abc.abstractmethod
    async def resend_verification(self, verify: dtos.ResendVerificationDTO ):
        ...

    @abc.abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> str:
        ...

    @abc.abstractmethod
    async def request_password_reset(self, password_reset: dtos.RequestPasswordResetDTO):
        ...

    @abc.abstractmethod
    async def reset_password(self, reset_password: dtos.ResetPasswordDTO): ...


class AuthService(AbstractAuthService):


    def __init__(self, uow: UnitOfWork, token_handler: AbstractTokenHandler, password_handler: AbstractPasswordHandler):
        self._uow = uow
        self._token_handler = token_handler
        self._password_handler = password_handler

    async def login(self, email: str, password: str) -> typing.Dict:
        
        existing_user = await self._uow.user_auth_repository.get_user_auth_by_email(email=email)
        if (
            not existing_user or
            not self._password_handler.verify_password(
                password=password, 
                hashed_password=existing_user.hashed_password
            )
        ):
            raise UnauthorizedException("Invalid email or password")
        
        return {
            "access_token":self._token_handler.create_access_token(
                user_id=existing_user.id
            ),
            "refresh_token": self._token_handler.create_refresh_token(
                user_id=existing_user.id
            ),
            "token_type": "bearer"
        }
    
    async def refresh_access_token(self, refresh_token: str) -> typing.Dict:
        
        payload = self._token_handler.decode_token(refresh_token)

        try:
            user_id = UUID(payload.get("user_id"))
        except (TypeError, ValueError):
            raise UnauthorizedException("Invalid refresh token")

        existing_user = await self._uow.user_repository.get_by_id(user_id=user_id)

        if not existing_user:
            raise UnauthorizedException("Invalid refresh token")
        
        return{
            "access_token": self._token_handler.create_access_token(
                user_id=existing_user.id
            )
        }

    async def verify_user(self, verify: dtos.VerifyUserDTO) -> None:

        existing_verify = await self._uow.user_auth_repository.get_user_verification_by_token(verification_token=verify.verification_token)
        
        if not existing_verify:
            raise NotFoundException("User verification token not found")

        if existing_verify.verified_at:
            raise  InvalidStateTransitionException("User is already verfied")

        if existing_verify.is_expired:
            raise TokenExpiredException("User verification token is expired")
        
        hashed_password = self._password_handler.hash_password(verify.password)

        await self._uow.user_auth_repository.save_user_verification(user_id = existing_verify.user_id, hashed_password=hashed_password, verified_at=datetime.now(tz=timezone.utc))


    async def resend_verification(self, verify: dtos.ResendVerificationDTO ) -> None:
        
        existing_verify = self._uow.user_auth_repository.get_user_verification_by_email(email=email)

        if not existing_verify:
            raise NotFoundException("User with this email not found")
        
        if existing_verify.verified_at:
            raise InvalidStateTransitionException("User already verfied cannot resend verification email")
        
        if not existing_verify.is_expired:
            raise VerificationCooldownException("Verfication email is already sent")
        
        verify = auth_domain.UserVerificationModel.resend_verification(
            user_id=existing_verify.user_id,
            email = verify.email,
            verification_token=secrets.token_urlsafe(32),
            verification_token_created_at=datetime.now(tz=datetime.timezone.utc)
        )
        self._uow.register_entity(verify)
        await self._uow.user_auth_repository.update_user_verification(verify=verify)

    async def request_password_reset(self, password_reset: dtos.RequestPasswordResetDTO):
        
        existing_password_reset = await self._uow.user_auth_repository.get_user_password_reset_request_by_email(email=password_reset.email)

        if not existing_password_reset:
            raise NotFoundException("User with this email not found")
        
        password_reset = auth_domain.UserPasswordResetModel.request_password_reset(
            user_id=existing_password_reset.user_id,
            email=existing_password_reset.email,
            new_password_verification_token=secrets.token_urlsafe(32),
            new_password_verification_token_created_at=datetime.now(tz=datetime.timezone.utc)
        )

        if password_reset.is_expired:
            raise TokenExpiredException("User reset password verification token is expired")

        self._uow.register_entity(password_reset)
        self._uow.user_auth_repository.save_user_new_password_verification(password_reset=password_reset)

    async def reset_password(self, reset_password: dtos.ResetPasswordDTO):

        existing_password_reset = await self._uow.user_auth_repository.get_user_password_reset_request_by_email(email=password_reset.email)

        if not existing_password_reset:
            raise NotFoundException("User password request not found")
        
        if existing_password_reset.is_expired:
            raise VerificationCooldownException("Password reset verfication email is already sent")

        hashed_password = self._password_handler.hash_password(password=reset_password.password)

        await self._uow.user_auth_repository.update_password(user_id=existing_password_reset.user_id, hashed_password=hashed_password)