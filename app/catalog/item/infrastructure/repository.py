import abc
from uuid import UUID
from sqlalchemy import select, exists
from catalog.item.infrastructure.orm import ItemORM


class AbstractItemRepository(abc.ABC):


    @abc.abstractmethod
    async def exists_item_group_id_in_items(self, item_group_id: UUID) -> bool : ...


class ItemRepository(AbstractItemRepository):


    def __init__(self, session):
        self._session = session

    async def exists_item_group_id_in_items(self, item_group_id: UUID) -> bool :

        is_exists = (
            await self._session.scalar(
                select(
                    exists()
                    .where(ItemORM.group_id == item_group_id)
                )
            )
        )

        return is_exists