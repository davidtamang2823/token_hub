import asyncio
import logging
import csv
from pathlib import Path
from sqlalchemy import select
from core.database import AsyncSessionLocal
from accounts.role_permission.infrastructure.orm import Permission

async def seed_permissions():
    file_path = Path(__file__).parent / "permissions.csv"
    async with AsyncSessionLocal() as session:
        try:
            stmt = select(Permission.codename)
            result = await session.execute(stmt)
            existing_permissions = result.scalars().all()
            new_permissions_to_create = []
            with open(file_path, newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["codename"] not in existing_permissions:               
                        new_permissions_to_create.append(
                            Permission(
                                codename=row["codename"],
                                name=row["name"],
                                is_super_admin_permission=row["is_super_admin_permission"] == "true",
                                description=row["description"]
                            )
                        )
                        logging.info(f"Adding permission {row["name"]} ...")
                    else:
                        logging.info(f"Skipping permission {row["name"]}, It already exists ...")
            if new_permissions_to_create:
                session.add_all(new_permissions_to_create)
                await session.commit()
                logging.info("All new permission created successfully ...")
        except Exception as e:
            await session.rollback()
            logging.exception(str(e))


if __name__ == "__main__":
    asyncio.run(seed_permissions())