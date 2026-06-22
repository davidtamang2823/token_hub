import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from core.database import AsyncSessionLocal
from core.constants.roles import STAFF_DEFAULT_ROLE
from accounts.role_permission.infrastructure.orm import Role, RolePermission, Permission


async def seed_roles_with_permission():
    async with AsyncSessionLocal() as session:
        try:
            stmt = select(Role).where(
                Role.name == STAFF_DEFAULT_ROLE["name"],
                Role.tenant_id.is_(None),
            ).options(selectinload(Role.permissions))
            result = await session.execute(stmt)
            existing_role = result.scalar_one_or_none()

            stmt = select(Permission).where(Permission.name.in_(STAFF_DEFAULT_ROLE["permissions"]))
            result = await session.execute(stmt)
            permission_orm_objs = list(result.scalars().all())

            if not existing_role:
                logging.info(f"Seeding role '{STAFF_DEFAULT_ROLE['name']}' with {len(permission_orm_objs)} permissions.")
                new_role = Role(
                    name=STAFF_DEFAULT_ROLE["name"], 
                    tenant_id=None, 
                    is_system_role=STAFF_DEFAULT_ROLE["is_system_role"]
                )
                new_role.permissions = permission_orm_objs
                session.add(new_role)
            else:
                logging.info(f"Role '{STAFF_DEFAULT_ROLE['name']}' already exists. Skipping.")
                logging.info("Sedding new permission in existing role.")
                existing_role.permissions = permission_orm_objs

            await session.commit()
            logging.info("Finished seeding roles with permissions.")

        except Exception:
            await session.rollback()
            logging.exception("Error seeding roles with permissions.")


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_roles_with_permission())