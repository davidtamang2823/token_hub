import typing
from fastapi import APIRouter, Request, Depends, HTTPException, status
from accounts.auth.presentation.dependencies import get_auth_service
from accounts.auth.application import exceptions as auth_service_exceptions
from accounts.auth.application.services import AbstractAuthService
from core import exceptions as core_exceptions

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
async def login(request: Request, auth_service: typing.Annotated[AbstractAuthService, Depends(get_auth_service)]):

    request_data = await request.json()
    response_data = await auth_service.login(
        email=request_data.get("email", "").strip(),
        password=request_data.get("password", "").strip()
    )
    return response_data

@router.post("/refresh")
async def refresh(request: Request, auth_service: typing.Annotated[AbstractAuthService, Depends(get_auth_service)]):

    request_data = await request.json()
    response_data = await auth_service.refresh_access_token(
        refresh_token= request_data.get("refresh_token")
    )
    return response_data
