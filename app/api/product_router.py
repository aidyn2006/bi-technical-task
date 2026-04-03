import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.product_repo import ProductRepository
from app.schemas.product import ProductCreate, ProductListOut, ProductOut
from app.services.product_service import ProductService
from app.utils.pagination import PaginationParams, get_pagination

router = APIRouter(prefix="/products", tags=["Products"])


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(ProductRepository(db))


@router.get("/", response_model=ProductListOut)
async def list_products(
    request: Request,
    category: str | None = Query(default=None),
    min_price: Decimal | None = Query(default=None, gt=0),
    max_price: Decimal | None = Query(default=None, gt=0),
    search: str | None = Query(default=None, min_length=1),
    sort_by: str = Query(default="name", pattern="^(name|price)$"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    pagination: PaginationParams = Depends(get_pagination),
    service: ProductService = Depends(get_product_service),
) -> ProductListOut:
    return await service.get_list(
        request,
        category=category,
        min_price=min_price,
        max_price=max_price,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get("/{product_id}/", response_model=ProductOut)
async def get_product(
    product_id: uuid.UUID,
    service: ProductService = Depends(get_product_service),
) -> ProductOut:
    return await service.get_detail(product_id)


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    service: ProductService = Depends(get_product_service),
    _: User = Depends(get_current_user),
) -> ProductOut:
    return await service.create(payload)
