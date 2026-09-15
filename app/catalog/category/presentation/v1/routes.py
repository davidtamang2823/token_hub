from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from core.constants.permissions import CAN_CREATE_CATEGORY, CAN_VIEW_CATEGORY, CAN_UPDATE_CATEGORY, CAN_DELETE_CATEGORY
from core.dependencies import require_permission
from core.pagination import Pagination, DEFAULT_PAGE, DEFAULT_PAGE_SIZE
from catalog.category.application.services import AbstractCategoryService
from catalog.category.presentation.dependencies import get_category_service
from catalog.category.presentation.schemas import CategorySchema
from catalog.category.application.dtos import CreateCategoryDTO, UpdateCategoryDTO


router = APIRouter(prefix="/categories", tags=["Category API's"])

@router.get("", dependencies=[Depends(require_permission([CAN_VIEW_CATEGORY]))], response_model=Pagination)
async def list_category(
    request:Request, 
    category_service: Annotated[AbstractCategoryService, Depends(get_category_service)],
    q: str | None = None,
    page: int = DEFAULT_PAGE,
    page_size: int = DEFAULT_PAGE_SIZE
):
    category_filters = {
        "q": q
    }

    total, categories = await category_service.list_category(category_filters, page, page_size)
    paginated_data = Pagination(
        page = page,
        page_size = page_size,
        total = total,
        data=[
            CategorySchema(
                id = category.id,
                name=category.name,
                description=category.description
            )
            for category in categories
        ]
    )

    return paginated_data

@router.get("/{category_id}", dependencies=[Depends(require_permission([CAN_VIEW_CATEGORY]))], response_model=CategorySchema)
async def retrieve_category(
    request: Request, 
    category_id: UUID, 
    category_service: Annotated[AbstractCategoryService, Depends(get_category_service)]
):
    response_data = await category_service.retrieve_category(category_id)
    return response_data


@router.post("/", dependencies=[Depends(require_permission([CAN_CREATE_CATEGORY]))], response_model=CategorySchema)
async def create_category(
    request: Request,
    create_category: CreateCategoryDTO,
    category_service: Annotated[AbstractCategoryService, Depends(get_category_service)]
):
    response_data = await category_service.create_category(create_category)
    return response_data


@router.put("/{category_id}", dependencies=[Depends(require_permission([CAN_UPDATE_CATEGORY]))], response_model=CategorySchema)
async def update_category(
    request: Request,
    category_id: UUID,
    update_category: UpdateCategoryDTO,
    category_service: Annotated[AbstractCategoryService, Depends(get_category_service)]
):
    response_data = await category_service.update_category(update_category)
    return response_data

@router.delete("/{category_id}", dependencies=[Depends(require_permission([CAN_DELETE_CATEGORY]))])
async def delete_category(
    request: Request,
    category_id: UUID,
    category_service: Annotated[AbstractCategoryService, Depends(get_category_service)]
):
    await category_service.delete_category(category_id)
    return {"message": "Category deleted successfully."}