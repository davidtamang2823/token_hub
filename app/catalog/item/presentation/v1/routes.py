from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from core.dependencies import require_permission
from core.pagination import Pagination, DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from core.constants.permissions import CAN_ADD_ITEM, CAN_UPDATE_ITEM, CAN_VIEW_ITEM, CAN_DELETE_ITEM
from catalog.item.presentation.dependencies import get_item_service
from catalog.item.application.services import AbstractItemService
from catalog.item.application.dtos import CreateItemDTO, UpdateItemDTO, UpdateItemAvailabilityDTO

router = APIRouter(prefix="/items", tags=["Items API"])

@router.get("", dependencies=[Depends(require_permission(CAN_VIEW_ITEM))])
async def list_item(
    item_service: Annotated[AbstractItemService, Depends(get_item_service)],
    q: str = None,
    is_active: bool = None,
    is_available: bool = None,
    category_ids: Annotated [list[UUID] | None, Query()] = None,
    item_group_ids: Annotated [list[UUID] | None, Query()] = None,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE
) -> Pagination:

    item_filters = {
        "q": q,
        "is_active": is_active,
        "is_available": is_available,
        "category_ids": category_ids,
        "item_group_ids": item_group_ids
    }

    total, items = await item_service.list_item(item_filters=item_filters, page=page, page_size=page_size)

    return Pagination(
        total = total,
        page = page,
        page_size = page_size,
        data = items
    )

@router.get("/options", dependencies=[Depends(require_permission(CAN_VIEW_ITEM))])
async def list_option_item(
    item_service: Annotated[AbstractItemService, Depends(get_item_service)],
    category_ids: Annotated [list[UUID] | None, Query()] = None,
    item_group_ids: Annotated [list[UUID] | None, Query()] = None,
    q: str = None,
):
    item_filters = {
        "q": q,
        "category_ids": category_ids,
        "item_group_ids": item_group_ids
    }

    response_data = await item_service.list_option_item(item_filters=item_filters)
    return response_data

@router.get("/{item_id}", dependencies=[Depends(require_permission(CAN_VIEW_ITEM))])
async def retrieve_item(
    item_id: UUID,
    item_service: Annotated[AbstractItemService, Depends(get_item_service)]
):
    response_data = await item_service.retrieve_item(item_id=item_id)
    return response_data


@router.post("", dependencies=[Depends(require_permission(CAN_ADD_ITEM))])
async def create_item(
    create_item: CreateItemDTO,
    item_service: Annotated[AbstractItemService, Depends(get_item_service)]
):

    response_data = await item_service.create_item(create_item)
    return response_data


@router.put("", dependencies=[Depends(require_permission(CAN_UPDATE_ITEM))])
async def update_item(
    update_item: UpdateItemDTO,
    item_service: Annotated[AbstractItemService, Depends(get_item_service)]
):

    response_data = await item_service.update_item(update_item)
    return response_data


@router.patch("/set-item-availability", dependencies=[Depends(require_permission(CAN_UPDATE_ITEM))])
async def set_item_availability(
    update_item_availability: UpdateItemAvailabilityDTO,
    item_service: Annotated[AbstractItemService, Depends(get_item_service)]
):
    await item_service.set_item_availability(update_item_availability=update_item_availability)
    return {"message": "Item availability updated"}


@router.delete("{item_id}", dependencies=[Depends(require_permission(CAN_UPDATE_ITEM))])
async def delete_item(
    item_id: UUID, 
    item_service: Annotated[AbstractItemService, Depends(get_item_service)]
):
    await item_service.delete_item(item_id=item_id)
    return {"message": "Item has been deleted"}