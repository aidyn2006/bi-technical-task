import uuid
from decimal import Decimal

from fastapi import HTTPException, Request, status

from app.repositories.product_repo import ProductRepository
from app.schemas.product import ProductCreate, ProductListOut, ProductOut
from app.utils.pagination import build_pagination_urls


class ProductService:
    def __init__(self, repo: ProductRepository) -> None:
        self.repo = repo

    async def get_list(
        self,
        request: Request,
        *,
        category: str | None,
        min_price: Decimal | None,
        max_price: Decimal | None,
        search: str | None,
        sort_by: str,
        sort_order: str,
        limit: int,
        offset: int,
    ) -> ProductListOut:
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="min_price must be <= max_price")

        total, products = await self.repo.get_list(
            category=category,
            min_price=min_price,
            max_price=max_price,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

        next_url, previous_url = build_pagination_urls(request, total, limit, offset)

        return ProductListOut(
            count=total,
            next=next_url,
            previous=previous_url,
            results=[ProductOut.model_validate(p) for p in products],
        )

    async def get_detail(self, product_id: uuid.UUID) -> ProductOut:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return ProductOut.model_validate(product)

    async def create(self, data: ProductCreate) -> ProductOut:
        product = await self.repo.create(data)
        return ProductOut.model_validate(product)
