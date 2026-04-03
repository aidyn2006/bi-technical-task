import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate


class ProductRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_list(
        self,
        *,
        category: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        search: str | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[int, list[Product]]:
        query = select(Product)

        if category:
            query = query.where(Product.category == category)
        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                Product.name.ilike(pattern) | Product.description.ilike(pattern)
            )

        count_result = await self.db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

        sort_col = Product.price if sort_by == "price" else Product.name
        sort_col = sort_col.desc() if sort_order == "desc" else sort_col.asc()
        query = query.order_by(sort_col).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return total, list(result.scalars().all())

    async def get_by_id(self, product_id: uuid.UUID) -> Product | None:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def create(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        self.db.add(product)
        await self.db.flush()
        return product
