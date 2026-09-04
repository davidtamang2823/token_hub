import typing
from fastapi import APIRouter, Request, Depends, HTTPException, status
from accounts.auth.presentation.dependencies import get_auth_service
from accounts.auth.application import exceptions as auth_service_exceptions
from accounts.auth.application.services import AbstractAuthService
from core import exceptions as core_exceptions
from accounts.auth.application import dtos
from core.constants.permissions import CAN_UPDATE_USER
from core.dependencies import require_permission

public_router = APIRouter(prefix="/auth", tags=["Auth (Public)"])
router = APIRouter(prefix="/auth", tags=["Auth"])
admin_router = APIRouter(prefix="/admin/auth", tags=["Auth"])

@public_router.post("/login")
async def login(request: Request, auth_service: typing.Annotated[AbstractAuthService, Depends(get_auth_service)]):

    request_data = await request.json()
    response_data = await auth_service.login(
        email=request_data.get("email", "").strip(),
        password=request_data.get("password", "").strip()
    )
    return response_data

@public_router.post("/refresh")
async def refresh(request: Request, auth_service: typing.Annotated[AbstractAuthService, Depends(get_auth_service)]):

    request_data = await request.json()
    response_data = await auth_service.refresh_access_token(
        refresh_token= request_data.get("refresh_token")
    )
    return response_data

@public_router.post("/verify-user")
async def verify_user(
    request: Request, 
    verify_user: dtos.VerifyUserDTO, 
    auth_service: typing.Annotated[AbstractAuthService, Depends(get_auth_service)]
):
    await auth_service.verify_user(verify=verify_user)
    return {"message": "User has been verified, please login"}

@router.post("/resend-user-verification", dependencies=[Depends(require_permission([CAN_UPDATE_USER]))])
@admin_router.post("/resend-user-verification", dependencies=[Depends(require_permission([CAN_UPDATE_USER]))])
async def resend_verification(
    request: Request,
    resend_verification: dtos.ResendVerificationDTO, 
    auth_service: typing.Annotated[AbstractAuthService, Depends(get_auth_service)]
):
    await auth_service.resend_verification(verify=resend_verification)
    return {"message": "User verification email has been sent"}

@public_router.post("/request-password-reset")
async def request_password_reset(
    request: Request, 
    request_password_reset: dtos.RequestPasswordResetDTO, 
    auth_service: typing.Annotated[AbstractAuthService, Depends(get_auth_service)]
):
    await auth_service.request_password_reset(request_password_reset)
    return {"message": "Password reset request has been sent"}

@public_router.post("/reset-password")
async def reset_password(
    request: Request, 
    reset_password: dtos.ResetPasswordDTO, 
    auth_service: typing.Annotated[AbstractAuthService, Depends(get_auth_service)]
):
    await auth_service.reset_password(reset_password)
    return {"message": "User password has been reset please login"}