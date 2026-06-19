from core.constants import permissions
from core.constants.roles import ADMIN
SYSTEM_ROLES = (
    {
        "name": ADMIN,
        "is_system_role": True,
        "permissions": [
            permissions.CAN_ADD_ITEM_FOR_ALL_TENANT,
            permissions.CAN_UPDATE_ITEM_OF_ALL_TENANT,
            permissions.CAN_VIEW_ITEM_OF_ALL_TENANT,
            permissions.CAN_DELETE_ITEM_OF_ALL_TENANT,
            permissions.CAN_ADD_ORDER_FOR_ALL_TENANT,
            permissions.CAN_UPDATE_ORDER_OF_ALL_TENANT,
            permissions.CAN_DELETE_ORDER_OF_ALL_TENANT,
            permissions.CAN_VIEW_ORDER_OF_ALL_TENANT,
            permissions.CAN_CREATE_USER_FOR_ALL_TENANT,
            permissions.CAN_UPDATE_USER_OF_ALL_TENANT,
            permissions.CAN_DELETE_USER_OF_ALL_TENANT,
            permissions.CAN_VIEW_USER_OF_ALL_TENANT,
            permissions.CAN_CREATE_ROLE_FOR_ALL_TENANT,
            permissions.CAN_UPDATE_ROLE_OF_ALL_TENANT,
            permissions.CAN_DELETE_ROLE_OF_ALL_TENANT,
            permissions.CAN_VIEW_ROLE_OF_ALL_TENANT,
            permissions.CAN_VIEW_ALL_PERMISSION,
            permissions.CAN_ADD_TENANT,
            permissions.CAN_UPDATE_ALL_TENANT,
            permissions.CAN_VIEW_ALL_TENANT,
            permissions.CAN_ADD_USER_TO_ALL_TENANT,
        ]
    },
)