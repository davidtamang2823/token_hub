from math import ceil
from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict, computed_field


DEFAULT_PAGE_SIZE = 10
DEFAULT_PAGE = 1

T = TypeVar("T")

class Pagination(BaseModel, Generic[T]):

    page_size: int
    page: int
    total: int
    data: list[T]


    @computed_field
    @property
    def total_page(self) -> int:
        return ceil(self.total/self.page_size) if self.total else 0

    @computed_field
    @property
    def has_next(self) -> bool:
        return self.page < self.total_page
    
    @computed_field
    @property
    def has_previous(self) -> bool:
        return self.page > 1

    model_config = ConfigDict(
        from_attributes=True
    )