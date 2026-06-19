import logging
from sqlalchemy import select
from accounts.role_permission.seeders.system_roles import SYSTEM_ROLES
from core.database import AsyncSessionLocal
from accounts.role_permission.infrastructure.orm import Role, RolePermission, Permission


async def seed_roles_with_permission():
    async with AsyncSessionLocal() as session:
        try:
            for role in SYSTEM_ROLES:
                stmt = select(Role.name).where(
                    Role.name == role["name"],
                    Role.tenant_id.is_(None),
                )
                result = await session.execute(stmt)
                existing_role = result.scalar_one_or_none()

                if existing_role:
                    logging.info(f"Role '{role['name']}' already exists. Skipping.")
                    continue

                stmt = select(Permission.id).where(Permission.name.in_(role["permissions"]))
                result = await session.execute(stmt)
                permission_ids = result.scalars().all()

                if len(permission_ids) != len(role["permissions"]):
                    found = set(permission_ids)
                    logging.warning(
                        f"Role '{role['name']}': expected {len(role['permissions'])} permissions, "
                        f"found {len(permission_ids)}. Some permissions may not be seeded yet."
                    )

                logging.info(f"Seeding role '{role['name']}' with {len(permission_ids)} permissions.")
                new_role = Role(name=role["name"], tenant_id=None, is_system_role=role["is_system_role"])
                session.add(new_role)
                await session.flush()

                role_permissions = [
                    RolePermission(role_id=new_role.id, permission_id=pid)
                    for pid in permission_ids
                ]
                session.add_all(role_permissions)

            await session.commit()
            logging.info("Finished seeding roles with permissions.")

        except Exception:
            await session.rollback()
            logging.exception("Error seeding roles with permissions.")


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_roles_with_permission())