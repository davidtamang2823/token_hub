#!/bin/sh
alembic upgrade head
python3 -m app.accounts.role_permission.seeders.seed_permissions
python3 -m app.accounts.role_permission.seeders.seed_roles_with_permission
python3 -m app.accounts.user.seeders.seed_user
fastapi dev --host 0.0.0.0 --port 8000