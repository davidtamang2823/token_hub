import abc
import typing
import jwt
from datetime import datetime, timezone, timedelta
from uuid import UUID
from pwdlib import PasswordHash
from core.exceptions import UnauthorizedException

class AbstractPasswordHandler(abc.ABC):
    @abc.abstractmethod
    def hash_password(self, password: str) -> str: ...

    @abc.abstractmethod
    def verify_password(self, password: str, hashed_password: str) -> bool: ...


class AbstractTokenHandler(abc.ABC):
    @abc.abstractmethod
    def create_access_token(self, user_id: UUID) -> str: ...

    @abc.abstractmethod
    def create_refresh_token(self, user_id: UUID) -> str: ...
    
    @abc.abstractmethod
    def decode_token(self, token: str) -> typing.Dict: ...


class PasswordHandler(AbstractPasswordHandler):
    def __init__(self) -> None:
        self._password_hash = PasswordHash.recommended()

    def hash_password(self, password: str) -> str:
        return self._password_hash.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self._password_hash.verify(password, hashed_password)


class TokenHandler(AbstractTokenHandler):
    def __init__(self, secret_key: str, algorithm: str, access_token_expire_minutes: int, refresh_token_expire_days: int) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(self, user_id: UUID) -> str:
        current_datetime = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "user_id": str(user_id),
            "type": "access",
            "iat": current_datetime,
            "exp": current_datetime + timedelta(minutes=self._access_token_expire_minutes)
        }
        return jwt.encode(
            payload=payload,
            key=self._secret_key,
            algorithm=self._algorithm
        )

    def create_refresh_token(self, user_id: UUID) -> str:
        current_datetime = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "user_id": str(user_id),
            "type": "refresh",
            "iat": current_datetime,
            "exp": current_datetime + timedelta(days=self._refresh_token_expire_days)
        }
        return jwt.encode(
            payload=payload,
            key=self._secret_key,
            algorithm=self._algorithm
        )

    def decode_token(self, token: str) -> typing.Dict:
        try:
            return jwt.decode(
                jwt=token,
                key=self._secret_key,
                algorithms=[self._algorithm],
            )
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("Invalid token")
