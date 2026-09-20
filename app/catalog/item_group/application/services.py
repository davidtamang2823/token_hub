import abc
from uuid import UUID

from catalog.item_group.domain.models import ItemGroupModel
from catalog.item_group.application.dtos import CreateItemGroupDTO, UpdateItemGroupDTO
from core.unit_of_work import UnitOfWork
from core.context import CurrentUser
from core.pagination import Pagination
from core.exceptions import NotFoundException, ErrorType, AlreadyExistsException, ResourceInUseError

class AbstractItemGroupService(abc.ABC):


    @abc.abstractmethod
    async def list_item_group(self, item_group_filters: dict, page: int, page_size: int) -> tuple[int, list[ItemGroupModel]]: ...

    @abc.abstractmethod
    async def retrieve_item_group(self, item_group_id: UUID) -> ItemGroupModel: ...  

    @abc.abstractmethod
    async def create_item_group(self, create_item_group: CreateItemGroupDTO) -> ItemGroupModel: ...

    @abc.abstractmethod
    async def update_item_group(self, update_item_group: UpdateItemGroupDTO) -> ItemGroupModel: ...

    @abc.abstractmethod
    async def delete_item_group(self, item_group_id: UUID) -> None: ...


class ItemGroupService(AbstractItemGroupService):

    def __init__(self, uow: UnitOfWork, current_user: CurrentUser):

        self._uow = uow
        self._current_user = current_user

    async def list_item_group(self, item_group_filters: dict, page: int, page_size: int) -> tuple[int, list[ItemGroupModel]]:

        item_group_filters["tenant_id"] = self._current_user.tenant_id
        offset = Pagination.get_offset(page, page_size)
        total, item_groups = await self._uow.item_group_repository.list_item_group(item_group_filters, offset, page_size)
        return total, item_groups

    async def retrieve_item_group(self, item_group_id: UUID) -> ItemGroupModel:

        item_group = await self._uow.item_group_repository.retrieve_item_group(
            item_group_id=item_group_id, 
            tenant_id=self._current_user.tenant_id
        )

        if not item_group:
            raise NotFoundException(
                f"Item group with id {item_group_id} not found", 
                ErrorType.ITEM_GROUP_NOT_FOUND
            )
        
        return item_group


    async def create_item_group(self, create_item_group: CreateItemGroupDTO) -> ItemGroupModel:

        item_group = ItemGroupModel.create(
            name = create_item_group.name,
            category_id=create_item_group.category_id,
            description= create_item_group.description,
            tenant_id= self._current_user.tenant_id,
            created_by_id= self._current_user.id
        )

        if not await self._uow.category_repository.exists_category_id(item_group.category_id, item_group.tenant_id):
            raise NotFoundException(
                f"Category with id {item_group.category_id} not found",
                ErrorType.CATEGORY_NOT_FOUND
            )


        if await self._uow.item_group_repository.exists_item_group_name(item_group.name, item_group.tenant_id, item_group.category_id):
            raise AlreadyExistsException(
                f"Cannot create, item group with this name {item_group.name} already exists", 
                ErrorType.ITEM_GROUP_ALREADY_EXISTS
            )
        
        await self._uow.item_group_repository.create_item_group(item_group)

        created_item_group = await self._uow.item_group_repository.retrieve_item_group(item_group.id, item_group.tenant_id)

        return created_item_group


    async def update_item_group(self, update_item_group: UpdateItemGroupDTO) -> ItemGroupModel:

        item_group = ItemGroupModel.update(
            item_group_id=update_item_group.id,
            category_id = update_item_group.category_id,
            name = update_item_group.name,
            description= update_item_group.description,
            tenant_id= self._current_user.tenant_id,
            updated_by_id= self._current_user.id
        )

        if not await self._uow.item_group_repository.exists_item_group_id(item_group.id, item_group.tenant_id):
            raise NotFoundException(
                f"Item Group with this id {item_group.id} not found",
                ErrorType.ITEM_GROUP_NOT_FOUND
            )

        if not await self._uow.category_repository.exists_category_id(item_group.category_id, item_group.tenant_id):
            raise NotFoundException(
                f"Category with id {item_group.category_id} not found",
                ErrorType.CATEGORY_NOT_FOUND
            )

        if await self._uow.item_group_repository.exists_item_group_name(item_group.name, item_group.tenant_id, item_group.category_id, item_group.id):
            raise AlreadyExistsException(
                f"Cannot update, item group with this name {item_group.name} already exists", 
                ErrorType.ITEM_GROUP_ALREADY_EXISTS
            )
        
        await self._uow.item_group_repository.update_item_group(item_group)

        updated_item_group = await self._uow.item_group_repository.retrieve_item_group(item_group.id, item_group.tenant_id)

        return updated_item_group


    async def delete_item_group(self, item_group_id: UUID) -> None:

        if not await self._uow.item_group_repository.exists_item_group_id(item_group_id, self._current_user.tenant_id):
            raise NotFoundException(
                f"Item group with this id {item_group_id} not found",
                ErrorType.ITEM_GROUP_NOT_FOUND
            )

        if await self._uow.item_repository.exists_item_group_id_in_items(item_group_id):
            raise ResourceInUseError(
                f"Item group {item_group_id} is still in use by one or more items", 
                ErrorType.ITEM_GROUP_IN_USE
            )

        await self._uow.item_group_repository.delete_item_group(item_group_id, self._current_user.tenant_id)