from fastapi import FastAPI, APIRouter, Request, status, Depends
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from core.middleware.authentication import JWTAuthenticationMiddleware
from core.security import TokenHandler
from core.config import settings
from core.exceptions import AppException, ErrorType

from accounts.auth.presentation.v1.routes import router as auth_router
from tenants.presentation.v1.routes import router as tenant_router, admin_router as tenant_admin_router
from accounts.role_permission.presentation.v1.routes import router as role_router, admin_router as role_admin_router

app = FastAPI()

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_type": exc.error_type,
            "message": exc.message,
        },
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error_type": ErrorType.VALIDATION_ERROR,
            "message": "Validation failed",
            "detail": exc.errors(include_url=False),
        },
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_type": ErrorType.INTERNAL_ERROR,
            "message": "An unexpected error occurred",
        },
    )

token_handler = TokenHandler(
    secret_key=settings.secret_key,
    algorithm=settings.jwt_algorithm,
    access_token_expire_minutes=settings.access_token_expire_minutes,
    refresh_token_expire_days=settings.refresh_token_expire_days
)

app.add_middleware(JWTAuthenticationMiddleware, token_handler=token_handler)

API_V1 = "/api/v1"

v1_router = APIRouter(prefix=API_V1)
v1_router.include_router(auth_router)
v1_router.include_router(tenant_router)
v1_router.include_router(role_router)

v1_admin_router = APIRouter(prefix=API_V1)
v1_admin_router.include_router(tenant_admin_router)
v1_admin_router.include_router(role_admin_router)

app.include_router(v1_router)
app.include_router(v1_admin_router)

