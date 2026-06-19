from fastapi import Depends
from accounts.auth.application.services import AuthService
from core.unit_of_work import UnitOfWork
from core.dependencies import get_unit_of_work
from core.security import TokenHandler, PasswordHandler
from core.config import settings


token_handler=TokenHandler(
    secret_key=settings.secret_key,
    algorithm=settings.jwt_algorithm,
    access_token_expire_minutes=settings.access_token_expire_minutes,
    refresh_token_expire_days=settings.refresh_token_expire_days
)
password_handler=PasswordHandler()

def get_auth_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> AuthService:
    return AuthService(
        uow=uow,
        token_handler=token_handler,
        password_handler=password_handler
    )
