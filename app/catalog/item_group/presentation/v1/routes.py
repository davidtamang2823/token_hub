from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from core.dependencies import require_permission
from core.constants.permissions import (
    CAN_CREATE_ITEM_GROUP,
    CAN_UPDATE_ITEM_GROUP,
    CAN_DELETE_ITEM_GROUP,
    CAN_VIEW_ITEM_GROUP
)
from core.pagination import Pagination, DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from catalog.item_group.application.services import AbstractItemGroupService
from catalog.item_group.presentation.dependencies import get_item_group_service
from catalog.item_group.application.read_models import ItemGroupReadModel
from catalog.item_group.application.dtos import CreateItemGroupDTO, UpdateItemGroupDTO


router = APIRouter(prefix="/item-groups", tags=["Item Groups API"])

@router.get("/{item_group_id}", dependencies=[Depends(require_permission([CAN_VIEW_ITEM_GROUP]))], response_model=ItemGroupReadModel)
async def retrieve_item_group(
    request: Request,
    item_group_id: UUID,
    item_group_service: Annotated[AbstractItemGroupService, Depends(get_item_group_service)]
):
    response_data = await item_group_service.retrieve_item_group(item_group_id=item_group_id)
    return response_data

@router.get("", dependencies=[Depends(require_permission([CAN_VIEW_ITEM_GROUP]))], response_model=Pagination)
async def retrieve_item_group(
    request: Request,
    item_group_service: Annotated[AbstractItemGroupService, Depends(get_item_group_service)],
    q: str | None = None,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE
):
    item_group_filters = {
        "q": q
    }

    total, item_groups = await item_group_service.list_item_group(item_group_filters, page, page_size)
    return Pagination(
        page = page,
        page_size = page_size,
        total = total,
        data=item_groups
    )

@router.post("", dependencies=[Depends(require_permission([CAN_CREATE_ITEM_GROUP]))], response_model=ItemGroupReadModel)
async def create_item_group(
    request: Request,
    create_item_group: CreateItemGroupDTO,
    item_group_service: Annotated[AbstractItemGroupService, Depends(get_item_group_service)]
):

    response_data = await item_group_service.create_item_group(create_item_group)
    return response_data

@router.put("/{item_group_id}", dependencies=[Depends(require_permission([CAN_UPDATE_ITEM_GROUP]))], response_model=ItemGroupReadModel)
async def update_item_group(
    request: Request,
    item_group_id: UUID,
    update_item_group: UpdateItemGroupDTO,
    item_group_service: Annotated[AbstractItemGroupService, Depends(get_item_group_service)]
):

    response_data = await item_group_service.update_item_group(update_item_group)
    return response_data

@router.delete("/{item_group_id}", dependencies=[Depends(require_permission([CAN_DELETE_ITEM_GROUP]))])
async def delete_item_group(
    request: Request,
    item_group_id: UUID,
    item_group_service: Annotated[AbstractItemGroupService, Depends(get_item_group_service)]
):

    await item_group_service.delete_item_group(item_group_id)
    return {"message": "Item group deleted successfully"}