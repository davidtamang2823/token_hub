# Tenant-scoped permissions (is_super_admin_permission = False)
# These are assigned to roles within a specific tenant.

CAN_ADD_ITEM = "can_add_item"
CAN_UPDATE_ITEM = "can_update_item"
CAN_VIEW_ITEM = "can_view_item"
CAN_DELETE_ITEM = "can_delete_item"

CAN_ADD_ORDER = "can_add_order"
CAN_UPDATE_ORDER = "can_update_order"
CAN_DELETE_ORDER = "can_delete_order"
CAN_VIEW_ORDER = "can_view_order"

CAN_CREATE_USER = "can_create_user"
CAN_UPDATE_USER = "can_update_user"
CAN_DELETE_USER = "can_delete_user"
CAN_VIEW_USER = "can_view_user"

CAN_CREATE_ROLE = "can_create_role"
CAN_UPDATE_ROLE = "can_update_role"
CAN_DELETE_ROLE = "can_delete_role"
CAN_VIEW_ROLE = "can_view_role"

CAN_VIEW_PERMISSION = "can_view_permission"

CAN_ADD_USER_TO_TENANT = "can_add_user_to_tenant"


# System (super admin) permissions (is_super_admin_permission = True)
# These are only assignable to system-level roles (tenant_id = NULL).

CAN_ADD_ITEM_FOR_ALL_TENANT = "can_add_item_for_all_tenant"
CAN_UPDATE_ITEM_OF_ALL_TENANT = "can_update_item_of_all_tenant"
CAN_VIEW_ITEM_OF_ALL_TENANT = "can_view_item_of_all_tenant"
CAN_DELETE_ITEM_OF_ALL_TENANT = "can_delete_item_of_all_tenant"

CAN_ADD_ORDER_FOR_ALL_TENANT = "can_add_order_for_all_tenant"
CAN_UPDATE_ORDER_OF_ALL_TENANT = "can_update_order_of_all_tenant"
CAN_DELETE_ORDER_OF_ALL_TENANT = "can_delete_order_of_all_tenant"
CAN_VIEW_ORDER_OF_ALL_TENANT = "can_view_order_of_all_tenant"

CAN_CREATE_USER_FOR_ALL_TENANT = "can_create_user_for_all_tenant"
CAN_UPDATE_USER_OF_ALL_TENANT = "can_update_user_of_all_tenant"
CAN_DELETE_USER_OF_ALL_TENANT = "can_delete_user_of_all_tenant"
CAN_VIEW_USER_OF_ALL_TENANT = "can_view_user_of_all_tenant"

CAN_CREATE_ROLE_FOR_ALL_TENANT = "can_create_role_for_all_tenant"
CAN_UPDATE_ROLE_OF_ALL_TENANT = "can_update_role_of_all_tenant"
CAN_DELETE_ROLE_OF_ALL_TENANT = "can_delete_role_of_all_tenant"
CAN_VIEW_ROLE_OF_ALL_TENANT = "can_view_role_of_all_tenant"

CAN_VIEW_ALL_PERMISSION = "can_view_all_permission"

CAN_ADD_TENANT = "can_add_tenant"
CAN_UPDATE_ALL_TENANT = "can_update_all_tenant" #Not needed
CAN_UPDATE_TENANT = "can_update_tenant"
CAN_VIEW_ALL_TENANT = "can_view_all_tenant"
CAN_ADD_USER_TO_ALL_TENANT = "can_add_user_to_all_tenant"
CAN_DELETE_TENANT = "can_delete_tenant"

# Grouped sets — useful for seeders and bulk permission checks.

TENANT_PERMISSIONS: frozenset[str] = frozenset({
    CAN_ADD_ITEM,
    CAN_UPDATE_ITEM,
    CAN_VIEW_ITEM,
    CAN_DELETE_ITEM,
    CAN_ADD_ORDER,
    CAN_UPDATE_ORDER,
    CAN_DELETE_ORDER,
    CAN_VIEW_ORDER,
    CAN_CREATE_USER,
    CAN_UPDATE_USER,
    CAN_DELETE_USER,
    CAN_VIEW_USER,
    CAN_CREATE_ROLE,
    CAN_UPDATE_ROLE,
    CAN_DELETE_ROLE,
    CAN_VIEW_ROLE,
    CAN_VIEW_PERMISSION,
    CAN_ADD_USER_TO_TENANT,
})

SYSTEM_PERMISSIONS: frozenset[str] = frozenset({
    CAN_ADD_ITEM_FOR_ALL_TENANT,
    CAN_UPDATE_ITEM_OF_ALL_TENANT,
    CAN_VIEW_ITEM_OF_ALL_TENANT,
    CAN_DELETE_ITEM_OF_ALL_TENANT,
    CAN_ADD_ORDER_FOR_ALL_TENANT,
    CAN_UPDATE_ORDER_OF_ALL_TENANT,
    CAN_DELETE_ORDER_OF_ALL_TENANT,
    CAN_VIEW_ORDER_OF_ALL_TENANT,
    CAN_CREATE_USER_FOR_ALL_TENANT,
    CAN_UPDATE_USER_OF_ALL_TENANT,
    CAN_DELETE_USER_OF_ALL_TENANT,
    CAN_VIEW_USER_OF_ALL_TENANT,
    CAN_CREATE_ROLE_FOR_ALL_TENANT,
    CAN_UPDATE_ROLE_OF_ALL_TENANT,
    CAN_DELETE_ROLE_OF_ALL_TENANT,
    CAN_VIEW_ROLE_OF_ALL_TENANT,
    CAN_VIEW_ALL_PERMISSION,
    CAN_ADD_TENANT,
    CAN_UPDATE_ALL_TENANT,
    CAN_VIEW_ALL_TENANT,
    CAN_ADD_USER_TO_ALL_TENANT,
})