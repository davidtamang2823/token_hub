from typing import Annotated
from fastapi import Depends
from core.unit_of_work import UnitOfWork
from core.context import CurrentUser
from core.dependencies import get_unit_of_work, get_current_user
from catalog.item.application.services import AbstractItemService, ItemService

async def get_item_service(
    uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> AbstractItemService:

    return ItemService(
        uow=uow,
        current_user=current_user
    )