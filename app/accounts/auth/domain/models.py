from datetime import datetime, timedelta, timezone
from uuid import UUID
from pydantic import EmailStr
from core.domain import DomainModel, AggregateRoot
from accounts.auth.domain.events import UserResendVerificationEvent, PasswordResetVerificationEvent

EMAIL_VERIFICATION_TOKEN_EXPIRE_DAYS=1
PASSWORD_RESET_VERIFICATION_TOKEN_EXPIRE_MINUTES=15

class UserVerificationModel(AggregateRoot):

    user_id: UUID
    email: EmailStr
    verification_token: str
    verification_token_created_at: datetime
    verified_at: datetime | None = None

    @property
    def is_expired(self) -> bool:
        deadline = self.verification_token_created_at + timedelta(days=EMAIL_VERIFICATION_TOKEN_EXPIRE_DAYS)
        return datetime.now(tz=timezone.utc) > deadline

    @classmethod
    def resend_verification(cls, user_id: UUID, email: str, verification_token: str, verification_token_created_at: datetime) -> "UserVerficationModel":

        return cls(
            user_id = user_id,
            email = email,
            verification_token = verification_token,
            verification_token_created_at = verification_token_created_at,
            events = [
                UserResendVerificationEvent(
                    send_to=email,
                    verification_token=verification_token
                )
            ]
        )

class UserPasswordResetModel(AggregateRoot):

    user_id: UUID
    email: EmailStr
    new_password_verification_token: str | None = None
    new_password_verification_token_created_at: datetime | None = None

    @property
    def is_expired(self) -> bool:
        if self.new_password_verification_token_created_at:
            deadline = self.new_password_verification_token_created_at + timedelta(minutes=PASSWORD_RESET_VERIFICATION_TOKEN_EXPIRE_MINUTES)
            return datetime.now(tz=timezone.utc) > deadline
        return False

    @classmethod
    def request_password_reset(cls, user_id: UUID, email: str, new_password_verification_token: str, new_password_verification_token_created_at: datetime) -> "UserPasswordResetModel":
        return cls(
            user_id = user_id,
            email = email,
            new_password_verification_token = new_password_verification_token,
            new_password_verification_token_created_at = new_password_verification_token_created_at,
            events = [
                PasswordResetVerificationEvent(
                    send_to=email,
                    new_password_verification_token=new_password_verification_token
                )
            ]
        )

class UserAuthModel(DomainModel):

    id: UUID
    hashed_password: str
    is_staff: bool
    is_active: bool
    verified_at: datetime | None = None