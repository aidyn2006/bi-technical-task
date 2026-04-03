import uuid
from decimal import Decimal

from fastapi import HTTPException, status

from app.models.cart import Cart
from app.models.user import User
from app.repositories.cart_repo import CartRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.cart import CartItemCreate, CartItemOut, CartItemUpdate, CartOut


class CartService:
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository) -> None:
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    async def _get_or_create_cart(self, user: User | None, session_id: str | None) -> Cart:
        if user:
            return await self.cart_repo.get_or_create_for_user(user.id)
        if session_id:
            return await self.cart_repo.get_or_create_for_session(session_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide Authorization header or X-Session-ID")

    async def _get_cart(self, user: User | None, session_id: str | None) -> Cart:
        if user:
            cart = await self.cart_repo.get_by_user_id(user.id)
        elif session_id:
            cart = await self.cart_repo.get_by_session(session_id)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide Authorization header or X-Session-ID")
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
        return cart

    async def add_item(self, user: User | None, session_id: str | None, payload: CartItemCreate) -> CartOut:
        product = await self.product_repo.get_by_id(payload.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        cart = await self._get_or_create_cart(user, session_id)
        await self.cart_repo.add_item(cart.id, payload.product_id, payload.quantity)
        return await self._build_cart_out(user, session_id)

    async def get_cart(self, user: User | None, session_id: str | None) -> CartOut:
        await self._get_cart(user, session_id)
        return await self._build_cart_out(user, session_id)

    async def update_item(self, user: User | None, session_id: str | None, item_id: uuid.UUID, payload: CartItemUpdate) -> CartOut:
        cart = await self._get_cart(user, session_id)
        item = await self.cart_repo.get_item(item_id)
        if not item or item.cart_id != cart.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
        await self.cart_repo.update_item(item, payload.quantity)
        return await self._build_cart_out(user, session_id)

    async def delete_item(self, user: User | None, session_id: str | None, item_id: uuid.UUID) -> None:
        cart = await self._get_cart(user, session_id)
        item = await self.cart_repo.get_item(item_id)
        if not item or item.cart_id != cart.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
        await self.cart_repo.delete_item(item)

    async def _build_cart_out(self, user: User | None, session_id: str | None) -> CartOut:
        cart = await self._get_cart(user, session_id)
        total = sum(Decimal(str(item.product.price)) * item.quantity for item in cart.items)
        return CartOut(
            id=cart.id,
            session_id=cart.session_id,
            items=[CartItemOut.model_validate(i) for i in cart.items],
            total_price=total,
        )
