import logging
import datetime
from sqlalchemy import select
from core.database import AsyncSessionLocal
from core.security import PasswordHandler
from accounts.user.infrastructure.orm import User, UserTenant
from accounts.role_permission.infrastructure.orm import Role
from core.constants.roles import ADMIN

password_handler = PasswordHandler()


async def seed_user(email: str, password: str, first_name: str, last_name: str, is_staff: bool = False, is_active: bool = False):
    async with AsyncSessionLocal() as session:
        try:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                logging.info(f"User '{email}' already exists. Skipping.")
                return

            stmt = select(Role).where(Role.name == ADMIN, Role.tenant_id.is_(None))
            result = await session.execute(stmt)
            admin_role = result.scalar_one_or_none()

            if not admin_role:
                logging.warning("Admin role not found. Seed roles before seeding users.")
                return

            hashed_password = password_handler.hash_password(password)
            new_user = User(
                email=email,
                password=hashed_password, 
                first_name=first_name,
                last_name=last_name, 
                is_staff=is_staff, 
                is_active=is_active,
                verified_at=datetime.datetime.now(tz=datetime.timezone.utc)
            )
            session.add(new_user)
            await session.flush()

            # tenant_id=None — system-level admin, not scoped to any tenant
            user_tenant = UserTenant(user_id=new_user.id, tenant_id=None, role_id=admin_role.id)
            session.add(user_tenant)

            await session.commit()
            logging.info(f"Admin user '{email}' created successfully.")

        except Exception:
            await session.rollback()
            logging.exception(f"Failed to seed admin user '{email}'.")


if __name__ == "__main__":
    import asyncio
    from core.config import settings
    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        seed_user(
            email=settings.admin_email, 
            password=settings.admin_password, 
            first_name=settings.admin_first_name, 
            last_name=settings.admin_last_name, 
            is_staff=True,
            is_active=True    
        )
    )