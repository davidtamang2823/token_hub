from pydantic import EmailStr
from core.domain import DomainModel

class VerifyUserDTO(DomainModel):
    password: str
    verification_token: str


class AuthenticationDTO(DomainModel):
    email: EmailStr
    password: str


class ResendVerificationDTO(DomainModel):
    email: EmailStr

class RequestPasswordResetDTO(DomainModel):
    email: EmailStr

class ResetPasswordDTO(DomainModel):
    new_password_verification_token: str
    password: str