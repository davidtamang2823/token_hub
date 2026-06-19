import abc
import typing
from uuid import UUID
from core.security import AbstractTokenHandler, AbstractPasswordHandler
from core.unit_of_work import UnitOfWork
from core.exceptions import UnauthorizedException

class AbstractAuthService(abc.ABC):


    @abc.abstractmethod
    async def login(self, email: str, password: str):
        ...
    
    @abc.abstractmethod
    async def verify_user(self, data: typing.Dict):
        ...

    @abc.abstractmethod
    async def resend_verification(self, email: str):
        ...

    @abc.abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> str:
        ...

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

    async def verify_user(self, data: typing.Dict):
        ...

    async def resend_verification(self, email: str):
        ...
