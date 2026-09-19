from typing import Annotated
from fastapi import Depends
from core.dependencies import get_current_user, get_unit_of_work
from core.context import CurrentUser
from core.unit_of_work import UnitOfWork
from catalog.item_group.application.services import AbstractItemGroupService, ItemGroupService


async def get_item_group_service(
    uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> AbstractItemGroupService:

    return ItemGroupService(
        uow,
        current_user
    )