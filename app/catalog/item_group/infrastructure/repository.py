import abc
from uuid import UUID
from sqlalchemy import select, exists
from catalog.item_group.infrastructure.orm import ItemGroupORM

class AbstractItemGroupRepository(abc.ABC):


    async def exists_category_id_in_item_groups(self, category_id: UUID) -> bool: ...


class ItemGroupRepository(AbstractItemGroupRepository):


    def __init__(self, session):

        self._session = session

    async def exists_category_id_in_item_groups(self, category_id: UUID) -> bool:

        is_exists = (
            await self._session.scalar(
                select(
                    exists()
                    .where(ItemGroupORM.category_id == category_id)
                )
            )
        ) 

        return is_exists