from core.constants import permissions

ADMIN = "ADMIN"

STAFF_DEFAULT_ROLE = {
    "name": ADMIN,
    "is_system_role": True,
    "permissions": permissions.STAFF_USER_PERMISSIONS
}


TENANT_DEFAULT_ROLE = {
    "name": ADMIN,
    "is_system_role": True,
    "permissions": permissions.USER_PERMISSIONS
}