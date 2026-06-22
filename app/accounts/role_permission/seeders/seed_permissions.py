import asyncio
import logging
import csv
from pathlib import Path
from sqlalchemy import select
from core.database import AsyncSessionLocal
from core.constants.permissions import ALL_PERMISSION_DETAILS
from accounts.role_permission.infrastructure.orm import Permission

async def seed_permissions():
    async with AsyncSessionLocal() as session:
        try:
            stmt = select(Permission.codename)
            result = await session.execute(stmt)
            existing_permissions = result.scalars().all()
            new_permissions_to_create = []
            for permission in ALL_PERMISSION_DETAILS:
                if permission.codename not in existing_permissions:               
                    new_permissions_to_create.append(
                        Permission(
                            codename=permission.codename,
                            name=permission.name,
                            description=permission.description
                        )
                    )
                    logging.info(f"Adding permission {permission.name} ...")
                else:
                    logging.info(f"Skipping permission {permission.name}, It already exists ...")
            if new_permissions_to_create:
                session.add_all(new_permissions_to_create)
                await session.commit()
                logging.info("All new permission created successfully ...")
        except Exception as e:
            await session.rollback()
            logging.exception(str(e))


if __name__ == "__main__":
    asyncio.run(seed_permissions())