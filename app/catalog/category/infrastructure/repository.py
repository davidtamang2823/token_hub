import abc
from sqlalchemy import delete, or_, func, exists
from catalog.category.domain.models import CategoryModel
from catalog.category.infrastructure.orm import CategoryORM

class AbstractCategoryRepository(abc.ABC):


    @abc.abstractmethod
    async def list_category(self, category_filters: dict, offset: int, limit: int) -> tuple[int, list[CategoryModel]]: ...

    @abc.abstractmethod
    async def retrieve_category(self, category_id: UUID, tenant_id: UUID) -> CategoryModel: ...

    @abc.abstractmethod
    async def exists_category_name(self, name: str, tenant_id: UUID, exclude_id: UUID | None = None) -> bool: ...

    @abc.abstractmethod
    async def exists_category_id(self, category_id: UUID, tenant_id: UUID) -> bool: ...

    @abc.abstractmethod
    async def create_category(self, create_category: CategoryModel) -> CategoryModel: ...

    @abc.abstractmethod
    async def update_category(self, update_category: CategoryModel) -> CategoryModel: ...

    @abc.abstractmethod
    async def delete_category(self, category_id: UUID, tenant_id: UUID) -> None: ...


class CategoryRepository(AbstractCategoryRepository):

    def __init__(self, session):
        self._session = session

    async def list_category(self, category_filters: dict, offset: int, limit: int) -> tuple[int, list[CategoryModel]]:

        tenant_id = category_filters.get("tenant_id")
        q = category_filters.get("q")

        stmt = (
            select(CategoryORM)
            .where(CategoryORM.tenant_id == tenant_id)
        )

        if q:
            stmt = stmt.where(CategoryORM.name.ilike(f"{q}%"))

        total = (
            await self._session.scalar(
                select(func.count()).select_from(stmt.subquery())
            )
        )

        category_orm_objs = (await self._session.execute(stmt)).scalars()

        categories = [
            self._create_category_model(category_orm_obj)
            for category_orm_obj in category_orm_objs
        ]

        return total, categories

    async def retrieve_category(self, category_id: UUID, tenant_id: UUID) -> CategoryModel:

        category_orm_obj = (
            await self._session.execute(
                select(CategoryORM)
                .where(
                    CategoryORM.tenant_id == tenant_id, 
                    CategoryORM.id == category_id
                )
            )
        ).scalar_one_or_none()

        if not category_orm_obj:
            return
        
        return self._create_category_model(category_orm_obj)


    async def exists_category_name(self, name: str, tenant_id: UUID, exclude_id: UUID | None = None) -> bool:

        stmt = (
            exists()
            .where(CategoryORM.name.ilike(name), CategoryORM.tenant_id == tenant_id)
        )

        if exclude_id:
            stmt = stmt.where(CategoryORM.id != exclude_id)

        is_exists = ( 
            await self._session.scalar(
                select(
                    stmt
                )
            )
        )
        return is_exists

    async def exists_category_id(self, category_id: UUID, tenant_id: UUID) -> bool:

        is_exists = ( 
            await self._session.scalar(
                select(
                    exists()
                    .where(
                        CategoryORM.id == category_id, 
                        CategoryORM.tenant_id == tenant_id
                    )                
                )
            )
        )
        return is_exists

    async def create_category(self, create_category: CategoryModel) -> CategoryModel:

        category_orm_obj = CategoryORM(
            id = create_category.id,
            name = create_category.name,
            description = create_category.description,
            tenant_id = create_category.tenant_id,
            created_by_id = create_category.created_by_id
        )

        self._session.add(category_orm_obj)

        return self._create_category_model(category_orm_obj)


    async def update_category(self, update_category: CategoryModel) -> CategoryModel:

        category_orm_obj = ( 
            await self._session.execute(
                select(CategoryORM)
                .where(
                    CategoryORM.tenant_id == update_category.tenant_id,
                    CategoryORM.id == update_category.id
                )
            )
        ).scalar_one_or_none()
        
        if not category_orm_obj:
            return
 
        category_orm_obj.name = update_category.name
        category_orm_obj.description = update_category.description
        category_orm_obj.updated_by_id = update_category.updated_by_id

        return self._create_category_model(category_orm_obj)

    async def delete_category(self, category_id: UUID, tenant_id: UUID) -> None:

        category_orm_obj = (
            await self._session.execute(
                select(CategoryORM)
                .where(
                    CategoryORM.tenant_id == tenant_id,
                    CategoryORM.id == category_id
                )
            )
        ).scalar_one_or_none()

        if category_orm_obj:
            self._session.delete(category_orm_obj)


    def _create_category_model(self, category_orm_obj: CategoryORM) -> CategoryModel:

        return CategoryModel(
            id = category_orm_obj.id,
            name = category_orm_obj.name,
            description = category_orm_obj.description,
            tenant_id = category_orm_obj.tenant_id
        )