import uuid
from decimal import Decimal

from fastapi import HTTPException, status

from app.repositories.cart_repo import CartRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.cart import CartItemCreate, CartItemOut, CartItemUpdate, CartOut


class CartService:
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository) -> None:
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    async def add_item(self, session_id: str, payload: CartItemCreate) -> CartOut:
        product = await self.product_repo.get_by_id(payload.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        cart = await self.cart_repo.get_or_create(session_id)
        await self.cart_repo.add_item(cart.id, payload.product_id, payload.quantity)

        return await self._build_cart_out(session_id)

    async def get_cart(self, session_id: str) -> CartOut:
        cart = await self.cart_repo.get_by_session(session_id)
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
        return await self._build_cart_out(session_id)

    async def update_item(self, session_id: str, item_id: uuid.UUID, payload: CartItemUpdate) -> CartOut:
        item = await self.cart_repo.get_item(item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
        if item.cart.session_id != session_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        await self.cart_repo.update_item(item, payload.quantity)
        return await self._build_cart_out(session_id)

    async def delete_item(self, session_id: str, item_id: uuid.UUID) -> None:
        item = await self.cart_repo.get_item(item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
        if item.cart.session_id != session_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        await self.cart_repo.delete_item(item)

    async def _build_cart_out(self, session_id: str) -> CartOut:
        cart = await self.cart_repo.get_by_session(session_id)
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

        total = sum(
            Decimal(str(item.product.price)) * item.quantity
            for item in cart.items
        )

        return CartOut(
            id=cart.id,
            session_id=cart.session_id,
            items=[CartItemOut.model_validate(i) for i in cart.items],
            total_price=total,
        )
