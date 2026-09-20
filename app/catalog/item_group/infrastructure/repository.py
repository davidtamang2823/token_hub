import abc
from uuid import UUID
from sqlalchemy import select, exists, func
from sqlalchemy.orm import selectinload 
from catalog.item_group.infrastructure.orm import ItemGroupORM
from catalog.item_group.domain.models import ItemGroupModel
from catalog.item_group.application.read_models import ItemGroupReadModel

class AbstractItemGroupRepository(abc.ABC):

    @abc.abstractmethod
    async def list_item_group(self, item_group_filters: dict, offset: int, limit: int) -> tuple[int, list[ItemGroupReadModel]]: ...

    @abc.abstractmethod
    async def retrieve_item_group(self, item_group_id: UUID, tenant_id: UUID) -> ItemGroupReadModel | None: ...

    @abc.abstractmethod
    async def exists_item_group_name(self, name: str, tenant_id: UUID, category_id: UUID, exclude_id: UUID | None = None) -> bool: ...

    @abc.abstractmethod
    async def exists_item_group_id(self, item_group_id: UUID, tenant_id: UUID) -> bool: ...

    @abc.abstractmethod
    async def exists_category_id_in_item_groups(self, category_id: UUID) -> bool: ...

    @abc.abstractmethod
    async def create_item_group(self, create_item_group: ItemGroupModel) -> ItemGroupModel: ...

    @abc.abstractmethod
    async def update_item_group(self, update_item_group: ItemGroupModel) -> ItemGroupModel: ...

    @abc.abstractmethod
    async def delete_item_group(self, item_group_id: UUID, tenant_id: UUID) -> None: ...



class ItemGroupRepository(AbstractItemGroupRepository):


    def __init__(self, session):

        self._session = session


    async def list_item_group(self, item_group_filters: dict, offset: int, limit: int) -> tuple[int, list[ItemGroupReadModel]]:

        tenant_id = item_group_filters.get("tenant_id")
        q = item_group_filters.get("q")
        category_id = item_group_filters.get("category_id")

        stmt = (
            select(ItemGroupORM)
            .options(selectinload(ItemGroupORM.category))
            .where(ItemGroupORM.tenant_id == tenant_id)
        )

        if q:
            stmt = stmt.where(ItemGroupORM.name.ilike(f"{q}%"))
        
        if category_id:
            stmt = stmt.where(ItemGroupORM.category_id == category_id)

        total = (
            await self._session.scalar(
                select(func.count()).select_from(stmt.subquery())
            )
        )

        item_group_orm_objs = ( await self._session.execute(stmt) ).scalars()
        item_groups = [
            ItemGroupReadModel(
                id = item_group_orm_obj.id,
                name = item_group_orm_obj.name,
                description = item_group_orm_obj.description,
                category_id = item_group_orm_obj.category_id,
                category_name = item_group_orm_obj.category.name
            )

            for item_group_orm_obj in item_group_orm_objs
        ]

        return total, item_groups

    async def retrieve_item_group(self, item_group_id: UUID, tenant_id: UUID) -> ItemGroupReadModel | None:

        item_group_orm_obj = (
            await self._session.execute(
                select(ItemGroupORM)
                .options(selectinload(ItemGroupORM.category))
                .where(ItemGroupORM.tenant_id == tenant_id, ItemGroupORM.id == item_group_id)
            )
        ).scalar_one_or_none()

        if item_group_orm_obj:
            return ItemGroupReadModel(
                id = item_group_orm_obj.id,
                name = item_group_orm_obj.name,
                description = item_group_orm_obj.description,
                category_id = item_group_orm_obj.category_id,
                category_name = item_group_orm_obj.category.name
            )

    async def exists_item_group_name(self, name: str, tenant_id: UUID, category_id: UUID, exclude_id: UUID | None = None) -> bool:

        stmt = (
            exists()
            .where(
                ItemGroupORM.tenant_id == tenant_id, 
                ItemGroupORM.category_id == category_id,  
                ItemGroupORM.name.ilike(name)
            )
        )

        if exclude_id:
            stmt = stmt.where(ItemGroupORM.id != exclude_id)

        is_exists = (
            await self._session.scalar(
                select(stmt)
            )
        )
        return is_exists

    async def exists_item_group_id(self, item_group_id: UUID, tenant_id: UUID) -> bool:
        is_exists = (
            await self._session.scalar(
                select(
                    exists()
                    .where(
                        ItemGroupORM.tenant_id == tenant_id, 
                        ItemGroupORM.id == item_group_id
                    )
                )
            )
        )
        return is_exists

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

    async def create_item_group(self, create_item_group: ItemGroupModel) -> ItemGroupModel:

        item_group_orm_obj = ItemGroupORM(
            id = create_item_group.id,
            name = create_item_group.name,
            description = create_item_group.description,
            category_id = create_item_group.category_id,
            tenant_id = create_item_group.tenant_id,
            created_by_id = create_item_group.created_by_id
        )

        self._session.add(item_group_orm_obj)
        await self._session.flush()

        return create_item_group

    async def update_item_group(self, update_item_group: ItemGroupModel) -> ItemGroupModel:

        item_group_orm_obj = (
            await self._session.execute(
                select(ItemGroupORM)
                .where(
                    ItemGroupORM.tenant_id == update_item_group.tenant_id,
                    ItemGroupORM.id == update_item_group.id
                )
            )
        ).scalar_one_or_none()

        if item_group_orm_obj:
            item_group_orm_obj.name = update_item_group.name
            item_group_orm_obj.description = update_item_group.description
            item_group_orm_obj.category_id = update_item_group.category_id
            item_group_orm_obj.updated_by_id = update_item_group.updated_by_id
            await self._session.flush()
            return update_item_group


    async def delete_item_group(self, item_group_id: UUID, tenant_id: UUID) -> None:

        item_group_orm_obj = (
            await self._session.execute(
                select(ItemGroupORM)
                .where(
                    ItemGroupORM.tenant_id == tenant_id,
                    ItemGroupORM.id == item_group_id
                )
            )
        ).scalar_one_or_none()

        if item_group_orm_obj:
            await self._session.delete(item_group_orm_obj)