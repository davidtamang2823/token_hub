from typing import Annotated
from fastapi import Depends
from core.unit_of_work import UnitOfWork
from core.context import CurrentUser
from core.dependencies import get_unit_of_work, get_current_user
from catalog.category.application.services import AbstractCategoryService, CategoryService

def get_category_service(
    uow: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)]
) -> AbstractCategoryService:
    return CategoryService(
        uow,
        current_user
    )