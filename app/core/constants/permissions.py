from typing import NamedTuple

class Permission(NamedTuple):
    name: str
    codename: str
    description: str

# These are assigned to roles within a specific tenant.

CAN_ADD_ITEM = "can_add_item"
CAN_UPDATE_ITEM = "can_update_item"
CAN_VIEW_ITEM = "can_view_item"
CAN_DELETE_ITEM = "can_delete_item"

CAN_ADD_ORDER = "can_add_order"
CAN_UPDATE_ORDER = "can_update_order"
CAN_DELETE_ORDER = "can_delete_order"
CAN_VIEW_ORDER = "can_view_order"

CAN_UPDATE_USER = "can_update_user"
CAN_VIEW_USER = "can_view_user"

CAN_CREATE_ROLE = "can_create_role"
CAN_UPDATE_ROLE = "can_update_role"
CAN_DELETE_ROLE = "can_delete_role"
CAN_VIEW_ROLE = "can_view_role"

CAN_VIEW_BILL = "can_view_bill"
CAN_CREATE_BILL = "can_create_bill"

CAN_ADD_USER_TO_TENANT = "can_add_user_to_tenant"
CAN_REMOVE_USER_FROM_TENANT = "can_remove_user_from_tenant"


# These are only assignable to system-level roles (tenant_id = NULL).

CAN_ADD_TENANT = "can_add_tenant"
CAN_UPDATE_TENANT = "can_update_tenant"
CAN_VIEW_ALL_TENANT = "can_view_all_tenant"
CAN_ADD_USER_TO_ALL_TENANT = "can_add_user_to_all_tenant"
CAN_DELETE_TENANT = "can_delete_tenant"

# Grouped sets — useful for seeders and bulk permission checks.


USER_PERMISSIONS: frozenset[str] = frozenset({
    
    CAN_VIEW_ITEM,
    CAN_ADD_ITEM,
    CAN_UPDATE_ITEM,
    CAN_DELETE_ITEM, 
    
    CAN_VIEW_ORDER,
    CAN_ADD_ORDER,
    CAN_UPDATE_ORDER,
    CAN_DELETE_ORDER,
    
    CAN_UPDATE_USER,
    CAN_VIEW_USER,

    CAN_VIEW_ROLE,
    CAN_CREATE_ROLE,
    CAN_UPDATE_ROLE,
    CAN_DELETE_ROLE,

    CAN_REMOVE_USER_FROM_TENANT,
    CAN_ADD_USER_TO_TENANT,
})

STAFF_USER_PERMISSIONS: frozenset[str] = frozenset({
    CAN_VIEW_ROLE,
    CAN_CREATE_ROLE,
    CAN_UPDATE_ROLE,
    CAN_DELETE_ROLE,

    CAN_VIEW_ALL_TENANT,
    CAN_ADD_TENANT,
    CAN_UPDATE_TENANT,
    CAN_DELETE_TENANT,

    CAN_UPDATE_USER,
    CAN_VIEW_USER,

    CAN_REMOVE_USER_FROM_TENANT,
    CAN_ADD_USER_TO_TENANT
})



ALL_PERMISSION_DETAILS: frozenset[Permission] = frozenset(
    {
        Permission(
            name="Can view item",
            description="Allows viewing items in the tenant menu",
            codename=CAN_VIEW_ITEM,
        ),
        Permission(
            name="Can add item",
            description="Allows adding new items to the tenant menu",
            codename=CAN_ADD_ITEM,
        ),
        Permission(
            name="Can update item",
            description="Allows updating existing items in the tenant menu",
            codename=CAN_UPDATE_ITEM,
        ),
        Permission(
            name="Can delete item",
            description="Allows deleting items from the tenant menu",
            codename=CAN_DELETE_ITEM,
        ),
        Permission(
            name="Can view order",
            description="Allows viewing orders for the tenant",
            codename=CAN_VIEW_ORDER,
        ),
        Permission(
            name="Can add order",
            description="Allows creating new orders for the tenant",
            codename=CAN_ADD_ORDER,
        ),
        Permission(
            name="Can update order",
            description="Allows updating existing orders for the tenant",
            codename=CAN_UPDATE_ORDER,
        ),
        Permission(
            name="Can delete order",
            description="Allows deleting orders for the tenant",
            codename=CAN_DELETE_ORDER,
        ),
        Permission(
            name="Can update user",
            description="Allows updating existing users within the tenant",
            codename=CAN_UPDATE_USER,
        ),
        Permission(
            name="Can view user",
            description="Allows viewing users within the tenant",
            codename=CAN_VIEW_USER,
        ),
        Permission(
            name="Can view role",
            description="Allows viewing roles within the tenant",
            codename=CAN_VIEW_ROLE,
        ),
        Permission(
            name="Can create role",
            description="Allows creating new roles within the tenant",
            codename=CAN_CREATE_ROLE,
        ),
        Permission(
            name="Can update role",
            description="Allows updating existing roles within the tenant",
            codename=CAN_UPDATE_ROLE,
        ),
        Permission(
            name="Can delete role",
            description="Allows deleting roles within the tenant",
            codename=CAN_DELETE_ROLE,
        ),
        Permission(
            name="Can add user to tenant",
            description="Allows adding existing users to the tenant",
            codename=CAN_ADD_USER_TO_TENANT,
        ),
        Permission(
            name="Can remove user from tenant",
            description="Allows removing users from the tenant",
            codename=CAN_REMOVE_USER_FROM_TENANT,
        ),
        Permission(
            name="Can view all tenant",
            description="Allows admin to view all tenants in the system",
            codename=CAN_VIEW_ALL_TENANT,
        ),
        Permission(
            name="Can add tenant",
            description="Allows admin to create new tenants in the system",
            codename=CAN_ADD_TENANT,
        ),
        Permission(
            name="Can update tenant",
            description="Allows staff user to update assigned tenants",
            codename=CAN_UPDATE_TENANT,
        ),
        Permission(
            name="Can delete tenant",
            description="Allows staff or admin to delete tenant",
            codename=CAN_DELETE_TENANT,
        ),
        Permission(
            name = "Can view bill",
            description="Allow user to view bill",
            codename = CAN_VIEW_BILL,
        ),
        Permission(
            name = "Can create bill",
            description="Allow user to create bill",
            codename = CAN_CREATE_BILL,
        )
    }
)

