import abc
from uuid import UUID
from core.unit_of_work import UnitOfWork
from core.context import CurrentUser
from core.exceptions import NotFoundException, ErrorType, AlreadyExistsException
from core.pagination import Pagination
from catalog.item.application.read_models import ItemReadModel
from catalog.item.application.dtos import CreateItemDTO, UpdateItemDTO, UpdateItemAvailabilityDTO
from catalog.item.domain.models import ItemModel


class AbstractItemService(abc.ABC):

    @abc.abstractmethod
    async def retrieve_item(self, item_id: UUID) -> ItemReadModel: ...

    @abc.abstractmethod
    async def list_item(self, item_filters: dict, page: int, page_size: int) -> tuple[int, list[ItemReadModel]]: ...

    @abc.abstractmethod
    async def list_option_item(self, item_filters: dict) -> list[ItemReadModel]: ...

    @abc.abstractmethod
    async def create_item(self, create_item: CreateItemDTO) -> ItemReadModel: ...

    @abc.abstractmethod
    async def update_item(self, update_item: UpdateItemDTO) -> ItemReadModel: ...

    @abc.abstractmethod
    async def set_item_availability(self, update_item_availability: UpdateItemAvailabilityDTO) -> None: ...

    @abc.abstractmethod
    async def delete_item(self, item_id: UUID) -> None: ...


class ItemService(AbstractItemService):

    def __init__(self, uow: UnitOfWork, current_user: CurrentUser):

        self._uow = uow
        self._current_user = current_user

    async def retrieve_item(self, item_id: UUID) -> ItemReadModel:

        item = await self._uow.item_repository.retrieve_item(item_id, self._current_user.tenant_id)
        if not item:
            raise NotFoundException(f"Item with id {item_id} does not exist", error_type=ErrorType.ITEM_NOT_FOUND)
        return item

    async def list_item(self, item_filters: dict, page: int, page_size: int) -> tuple[int, list[ItemReadModel]]:

        item_filters["tenant_id"] = self._current_user.tenant_id

        total_count, items = await self._uow.item_repository.list_item(item_filters, Pagination.get_offset(page, page_size), page_size)
        return total_count, items

    async def list_option_item(self, item_filters: dict) -> list[ItemReadModel]:

        item_filters["tenant_id"] = self._current_user.tenant_id
        item_filters["is_active"] = True
        item_filters["is_available"] = True
        
        _, items = await self._uow.item_repository.list_item(item_filters)
        return items


    async def create_item(self, create_item: CreateItemDTO) -> ItemReadModel:

        item = ItemModel.create(
            name = create_item.name,
            description = create_item.description,
            unit_price = create_item.unit_price,
            is_active = create_item.is_active,
            is_available = create_item.is_available,
            item_group_id = create_item.item_group_id,
            tenant_id = self._current_user.tenant_id,
            created_by_id = self._current_user.id
        )

        if not await self._uow.item_group_repository.exists_item_group_id(item_group_id=item.item_group_id, tenant_id=item.tenant_id):
            raise NotFoundException(f"Item group with id {item.item_group_id} does not exists", ErrorType.ITEM_GROUP_NOT_FOUND)

        if await self._uow.item_repository.exists_name_in_items(name=item.name, item_group_id=item.item_group_id, tenant_id=item.tenant_id):
            raise AlreadyExistsException(f"Item name {item.name} already exists", ErrorType.ITEM_ALREADY_EXISTS)

        await self._uow.item_repository.create_item(item)

        return await self._uow.item_repository.retrieve_item(item_id=item.id, tenant_id=item.tenant_id)



    async def update_item(self, update_item: UpdateItemDTO) -> ItemReadModel:

        item = ItemModel.update(
            item_id=update_item.id,
            name=update_item.name,
            description = update_item.description,
            unit_price = update_item.unit_price,
            is_active = update_item.is_active,
            is_available = update_item.is_available,
            item_group_id = update_item.item_group_id,
            tenant_id = self._current_user.tenant_id,
            updated_by_id = self._current_user.id
        )

        if not await self._uow.item_repository.exists_item_id(item_id=item.id, tenant_id=item.tenant_id):
            raise NotFoundException(f"Item with id {item.id} does not exists", ErrorType.ITEM_NOT_FOUND)

        if not await self._uow.item_group_repository.exists_item_group_id(item_group_id=item.item_group_id, tenant_id=item.tenant_id):
            raise NotFoundException(f"Item group with id {item.item_group_id} does not exists", ErrorType.ITEM_GROUP_NOT_FOUND)

        if await self._uow.item_repository.exists_name_in_items(name=item.name, item_group_id=item.item_group_id, tenant_id=item.tenant_id, exclude_item_id=item.id):
            raise AlreadyExistsException(f"Item name {item.name} already exists", ErrorType.ITEM_ALREADY_EXISTS)

        await self._uow.item_repository.update_item(item)

        return await self._uow.item_repository.retrieve_item(item_id=item.id, tenant_id=item.tenant_id)

    async def set_item_availability(self, update_item_availability: UpdateItemAvailabilityDTO) -> None:

        if not await self._uow.item_repository.exists_item_id(item_id=update_item_availability.id, tenant_id=self._current_user.tenant_id):
            raise NotFoundException(f"Item with id {item.id} does not exists", ErrorType.ITEM_NOT_FOUND)

        await self._uow.item_repository.update_availability(
            item_id=update_item_availability.id, 
            tenant_id=self._current_user.tenant_id, 
            is_available=update_item_availability.is_available
        )


    async def delete_item(self, item_id: UUID) -> None:

        if not await self._uow.item_repository.exists_item_id(item_id=item_id, tenant_id=self._current_user.tenant_id):
            raise NotFoundException(f"Item with id {item.id} does not exists", ErrorType.ITEM_NOT_FOUND)

        await self._uow.item_repository.delete_item(item_id=item_id)