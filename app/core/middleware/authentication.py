from uuid import UUID
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import AbstractTokenHandler
from core.config import settings
from core.database import AsyncSessionLocal
from core.context import CurrentUser
from core.exceptions import (
   UnauthorizedException,
   ErrorType
)

from accounts.user.infrastructure.orm import User, UserTenant
from accounts.role_permission.infrastructure.orm import Permission, RolePermission

EXEMPT_PATHS = {
    ("/api/v1/auth/login", "POST"),
    ("/api/v1/auth/verify", "POST"),
    ("/api/v1/auth/refresh", "POST"),
    ("/docs", "GET"),
    ("/redoc", "GET"),
    ("/openapi.json", "GET"),
}

class JWTAuthenticationMiddleware(BaseHTTPMiddleware):



    def __init__(self, app, token_handler: AbstractTokenHandler):
        super().__init__(app)
        self._token_handler = token_handler

    async def dispatch(self, request: Request, call_next):

        if self._is_exempt(request.url.path, request.method):
            return await call_next(request)

        token = self._extract_token(request)
        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error_type": ErrorType.UNAUTHORIZED,
                    "message": "Invalid token",
                }
            )

        try:
            payload = self._token_handler.decode_token(token)
            if payload.get("type") != "access":
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error_type": ErrorType.UNAUTHORIZED,
                        "message": "Invalid token type.",
                    }
                )
            try:
                tenant_id = UUID(request.headers.get("X-Tenant-ID"))
            except (TypeError, ValueError):
                tenant_id = None
            try:
                user_id = UUID(payload.get("user_id"))
            except (TypeError, ValueError):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error_type": ErrorType.UNAUTHORIZED,
                        "message": "Invalid token payload",
                    }
                )
            async with AsyncSessionLocal() as session:
                current_user = await self._get_current_user(session, user_id, tenant_id)
            if not current_user:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error_type": ErrorType.UNAUTHORIZED,
                        "message": "User not found",
                    }
                )

            if not current_user.is_active:
                if not current_user.verified_at:
                    message = "User not verified."
                else:
                    message = "User has been blocked."
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error_type": ErrorType.UNAUTHORIZED,
                        "message": message,
                    }
                )            
            request.state.current_user = current_user

        except UnauthorizedException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error_type": e.error_type,
                    "message": e.message,
                }
            )

        return await call_next(request)

    def _is_exempt(self, path: str, method: str) -> bool:
        return (path, method) in EXEMPT_PATHS

    def _extract_token(self, request: Request) -> str | None:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        return auth_header.split(" ", 1)[1]
    
    async def _get_current_user(self, session: AsyncSession, user_id: UUID, tenant_id: UUID | None = None) -> CurrentUser | None:
        stmt = (
            select(User).where(User.id == user_id)
        )
        result = await session.execute(stmt)
        user_orm_obj = result.scalar_one_or_none()

        if user_orm_obj is None:
            return None

        stmt = (
            select(Permission.codename, RolePermission.role_id)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(UserTenant, UserTenant.role_id == RolePermission.role_id)
            .where(UserTenant.user_id == user_id)
        )

        if user_orm_obj.is_staff:
            stmt = stmt.where(UserTenant.tenant_id == None)
        else:
            stmt = stmt.where(UserTenant.tenant_id == tenant_id)

        stmt = stmt.distinct()

        result = await session.execute(stmt)
        user_role_permissions = result.fetchall()
        permissions = [row[0] for row in user_role_permissions]

        return CurrentUser(
            id=user_orm_obj.id,
            is_active=user_orm_obj.is_active,
            is_staff=user_orm_obj.is_staff,
            permissions=permissions,
            tenant_id=tenant_id,
            role_id= user_role_permissions[0][1] if permissions else None,
            verified_at=user_orm_obj.verified_at
        )