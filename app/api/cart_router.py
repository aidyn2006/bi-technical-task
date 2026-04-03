import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_optional_session_id, get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.cart_repo import CartRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartOut
from app.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])


def get_cart_service(db: AsyncSession = Depends(get_db)) -> CartService:
    return CartService(CartRepository(db), ProductRepository(db))


@router.post("/", response_model=CartOut, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    payload: CartItemCreate,
    user: User | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_optional_session_id),
    service: CartService = Depends(get_cart_service),
) -> CartOut:
    return await service.add_item(user, session_id, payload)


@router.get("/", response_model=CartOut)
async def get_cart(
    user: User | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_optional_session_id),
    service: CartService = Depends(get_cart_service),
) -> CartOut:
    return await service.get_cart(user, session_id)


@router.put("/{item_id}/", response_model=CartOut)
async def update_cart_item(
    item_id: uuid.UUID,
    payload: CartItemUpdate,
    user: User | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_optional_session_id),
    service: CartService = Depends(get_cart_service),
) -> CartOut:
    return await service.update_item(user, session_id, item_id, payload)


@router.delete("/{item_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(
    item_id: uuid.UUID,
    user: User | None = Depends(get_optional_user),
    session_id: str | None = Depends(get_optional_session_id),
    service: CartService = Depends(get_cart_service),
) -> None:
    await service.delete_item(user, session_id, item_id)
