import abc
from uuid import UUID

from catalog.category.domain.models import CategoryModel
from catalog.category.application.dtos import CreateCategoryDTO, UpdateCategoryDTO
from core.unit_of_work import UnitOfWork
from core.context import CurrentUser
from core.exceptions import NotFoundException, ErrorType, AlreadyExistsException, ResourceInUseError

class AbstractCategoryService(abc.ABC):


    @abc.abstractmethod
    async def list_category(self, category_filters: dict, page: int, page_size: int) -> tuple[int, list[CategoryModel]]: ...

    @abc.abstractmethod
    async def retrieve_category(self, category_id: UUID) -> CategoryModel: ...  

    @abc.abstractmethod
    async def create_category(self, create_category: CreateCategoryDTO) -> CategoryModel: ...

    @abc.abstractmethod
    async def update_category(self, update_category: UpdateCategoryDTO) -> CategoryModel: ...

    @abc.abstractmethod
    async def delete_category(self, category_id: UUID) -> None: ...


class CategoryService(AbstractCategoryService):

    def __init__(self, uow: UnitOfWork, current_user: CurrentUser):

        self._uow = uow
        self._current_user = current_user

    async def list_category(self, category_filters: dict, page: int, page_size: int) -> tuple[int, list[CategoryModel]]:

        category_filters["tenant_id"] = self._current_user.tenant_id
        offset = Pagination.get_offset(page, page_size)
        total, categories = await self._uow.category_repository.list_category(category_filters, offset, page_size)
        return total, categories

    async def retrieve_category(self, category_id: UUID) -> CategoryModel:

        category = await self._uow.category_repository.retrieve_category(
            category_id=category_id, 
            tenant_id=self._current_user.tenant_id
        )

        if not category:
            raise NotFoundException(
                f"Category with id {category_id} not found", 
                ErrorType.CATEGORY_NOT_FOUND
            )
        
        return category


    async def create_category(self, create_category: CreateCategoryDTO) -> CategoryModel:

        category = CategoryModel.create(
            name = create_category.name,
            description= create_category.description,
            tenant_id= self._current_user.tenant_id,
            created_by_id= self._current_user.id
        )

        if await self._uow.category_repository.exists_category_name(category.name, category.tenant_id):
            raise AlreadyExistsException(
                f"Cannot create, category with this name {category.name} already exists", 
                ErrorType.CATEGORY_ALREADY_EXISTS
            )
        
        category = await self._uow.category_repository.create_category(category)

        return category


    async def update_category(self, update_category: UpdateCategoryDTO) -> CategoryModel:

        category = CategoryModel.update(
            category_id = update_category.id,
            name = create_category.name,
            description= create_category.description,
            tenant_id= self._current_user.tenant_id,
            updated_by_id= self._current_user.id
        )

        if not await self._uow.category_repository.exists_category_id(category.id, category.tenant_id):
            raise NotFoundException(
                f"Category with this id {category.id} not found",
                ErrorType.CATEGORY_NOT_FOUND
            )

        if await self._uow.category_repository.exists_category_name(category.name, category.tenant_id, category.id):
            raise AlreadyExistsException(
                f"Cannot update, category with this name {category.name} already exists", 
                ErrorType.CATEGORY_ALREADY_EXISTS
            )
        
        category = await self._uow.category_repository.update_category(category)

        return category


    async def delete_category(self, category_id: UUID) -> None:

        if not await self._uow.category_repository.exists_category_id(category_id, self._current_user.tenant_id):
            raise NotFoundException(
                f"Category with this id {category_id} not found",
                ErrorType.CATEGORY_NOT_FOUND
            )

        if await self._uow.item_group_repository.exists_category_id(category_id):
            raise ResourceInUseError(
                f"Category {category_id} is still in use by one or more item groups", 
                ErrorType.CATEGORY_IN_USE
            )

        await self._uow.category_repository.delete_category(category_id, self._current_user.tenant_id)