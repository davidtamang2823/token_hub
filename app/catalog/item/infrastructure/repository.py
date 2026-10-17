import abc
from uuid import UUID
from sqlalchemy import select, exists, or_, func
from catalog.item.infrastructure.orm import ItemORM
from catalog.item.application.read_models import ItemReadModel
from catalog.item_group.infrastructure.orm import ItemGroupORM
from catalog.category.infrastructure.orm import CategoryORM
from catalog.item.domain.models import ItemModel

class AbstractItemRepository(abc.ABC):


    @abc.abstractmethod
    async def retrieve_item(self, item_id: UUID, tenant_id: UUID) -> ItemReadModel | None: ...

    @abc.abstractmethod
    async def list_item(self, item_filters: dict, offset: int = None, limit: int = None) -> tuple[int, list[ItemReadModel]]: ...

    @abc.abstractmethod
    async def exists_item_group_id_in_items(self, item_group_id: UUID) -> bool : ...

    @abc.abstractmethod
    async def exists_name_in_items(self, name: str, tenant_id: UUID, exclude_item_id: UUID | None = None) -> bool: ...

    @abc.abstractmethod
    async def exists_item_id(self, item_id: UUID, tenant_id: UUID) -> bool: ...

    @abc.abstractmethod
    async def create_item(self, create_item: ItemModel) -> ItemModel: ...

    @abc.abstractmethod
    async def update_item(self, update_item: ItemModel) -> ItemModel: ...

    @abc.abstractmethod
    async def update_availability(self, item_id: UUID, tenant_id: UUID, is_available: bool) -> None: ...

    @abc.abstractmethod
    async def delete_item(self, item_id: UUID) -> None: ...



class ItemRepository(AbstractItemRepository):


    def __init__(self, session):
        self._session = session

    async def retrieve_item(self, item_id: UUID, tenant_id: UUID) -> ItemReadModel | None:

        item_orm_obj = (
            await self._session.execute(
                select(
                    ItemORM.id,
                    ItemORM.name,
                    ItemORM.description,
                    ItemORM.unit_price,
                    ItemORM.is_active,
                    ItemORM.is_available,
                    ItemORM.group_id,
                    ItemGroupORM.name.label("item_group_name"),
                    ItemGroupORM.category_id,
                    CategoryORM.name.label("category_name")
                )
                .join(ItemGroupORM, ItemORM.group_id == ItemGroupORM.id)
                .join(CategoryORM, ItemGroupORM.category_id == CategoryORM.id)
                .where(ItemORM.id == item_id, ItemORM.tenant_id == tenant_id)
            )
        ).one()

        if item_orm_obj is not None:
            print("==================================", item_orm_obj)
            return self._to_item_read_model(item_orm_obj)

    async def list_item(self, item_filters: dict, offset: int = None, limit: int = None) -> tuple[int, list[ItemReadModel]]:


        tenant_id = item_filters["tenant_id"]
        q = item_filters.get("q")
        is_active = item_filters.get("is_active")
        is_available = item_filters.get("is_available")
        category_ids = item_filters.get("category_ids")
        item_group_ids = item_filters.get("item_group_ids")

        stmt = (
            select(
                ItemORM.id,
                ItemORM.name,
                ItemORM.description,
                ItemORM.unit_price,
                ItemORM.is_active,
                ItemORM.is_available,
                ItemORM.group_id,
                ItemGroupORM.name.label("item_group_name"),
                ItemGroupORM.category_id,
                CategoryORM.name.label("category_name")
            )
            .join(ItemGroupORM, ItemORM.group_id == ItemGroupORM.id)
            .join(CategoryORM, ItemGroupORM.category_id == CategoryORM.id)
            .where(ItemORM.tenant_id == tenant_id)
        )

        if is_active is not None:
            stmt = stmt.where(ItemORM.is_active == is_active)

        if is_available is not None:
            stmt = stmt.where(ItemORM.is_available == is_available)


        if category_ids is not None:
            stmt = stmt.where(CategoryORM.id.in_(category_ids))

        if item_group_ids is not None:
            stmt = stmt.where(ItemGroupORM.id.in_(item_group_ids))

        if q:
            search_keys = q.split()
            for search_key in search_keys:
                stmt = stmt.where(
                    or_(
                        ItemORM.name.ilike(f"%{search_key}%"),
                        ItemGroupORM.name.ilike(f"%{search_key}%"),
                        CategoryORM.name.ilike(f"%{search_key}%")
                    )
                )
        
        total_count = await self._session.scalar(
            select(func.count()).select_from(stmt.subquery())
        )

        stmt = stmt.order_by(ItemORM.name).distinct()

        if offset is not None and limit is not None:
            stmt = stmt.offset(offset).limit(limit)
        
        item_orm_objs = (await self._session.execute(stmt)).fetchall()

        item_read_models = [self._to_item_read_model(item_orm_obj) for item_orm_obj in item_orm_objs]

        return total_count, item_read_models



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

    async def exists_name_in_items(self, name: str, item_group_id: UUID , tenant_id: UUID, exclude_item_id: UUID | None = None) -> bool:

        stmt = select(
            exists()
            .where(ItemORM.name == name, ItemORM.group_id == item_group_id, ItemORM.tenant_id == tenant_id)
        )

        if exclude_item_id is not None:
            stmt = stmt.where(ItemORM.id != exclude_item_id)

        is_exists = await self._session.scalar(stmt)

        return is_exists

    async def exists_item_id(self, item_id: UUID, tenant_id: UUID) -> bool:

        is_exists = (
            await self._session.scalar(
                select(
                    exists()
                    .where(ItemORM.id == item_id, ItemORM.tenant_id == tenant_id)
                )
            )
        )

        return is_exists

    async def create_item(self, create_item: ItemModel) -> ItemModel:

        item_orm_obj = ItemORM(
            id = create_item.id,
            name = create_item.name,
            description = create_item.description,
            unit_price = create_item.unit_price,
            is_active = create_item.is_active,
            is_available = create_item.is_available,
            group_id = create_item.item_group_id,
            tenant_id = create_item.tenant_id,
            created_by_id = create_item.created_by_id
        )

        self._session.add(item_orm_obj)
        await self._session.flush()

        return create_item

    async def update_item(self, update_item: ItemModel) -> ItemModel:
        
        item_orm_obj = (
            await self._session.execute(
                select(ItemORM)
                .where(ItemORM.id == update_item.id, ItemORM.tenant_id == update_item.tenant_id)
            )
        ).scalar_one_or_none()

        if item_orm_obj is not None:
            item_orm_obj.name = update_item.name
            item_orm_obj.description = update_item.description
            item_orm_obj.unit_price = update_item.unit_price
            item_orm_obj.is_active = update_item.is_active
            item_orm_obj.is_available = update_item.is_available
            item_orm_obj.group_id = update_item.item_group_id
            item_orm_obj.updated_by_id = update_item.updated_by_id

            await self._session.flush()

        return update_item


    async def update_availability(self, item_id: UUID, tenant_id: UUID, is_available: bool) -> None:

        item_orm_obj = (
            await self._session.execute(
                select(ItemORM)
                .where(ItemORM.id == item_id, ItemORM.tenant_id == tenant_id)
            )
        ).scalar_one_or_none()

        if item_orm_obj:
            item_orm_obj.is_available = is_available


    async def delete_item(self, item_id: UUID) -> None:

        item_orm_obj = await self._session.get(ItemORM, item_id)

        if item_orm_obj is not None:
            await self._session.delete(item_orm_obj)

    def _to_item_read_model(self, item_orm_obj: ItemORM) -> ItemReadModel:

        return ItemReadModel(
            id = item_orm_obj.id,
            name = item_orm_obj.name,
            description = item_orm_obj.description,
            unit_price = item_orm_obj.unit_price,
            is_active = item_orm_obj.is_active,
            is_available = item_orm_obj.is_available,
            item_group_id = item_orm_obj.group_id,
            item_group_name = item_orm_obj.item_group_name,
            category_id = item_orm_obj.category_id,
            category_name = item_orm_obj.category_name
        )