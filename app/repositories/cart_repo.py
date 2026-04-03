import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart, CartItem


class CartRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_session(self, session_id: str) -> Cart | None:
        result = await self.db.execute(
            select(Cart)
            .where(Cart.session_id == session_id)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
        )
        return result.scalar_one_or_none()

    async def create(self, session_id: str) -> Cart:
        cart = Cart(session_id=session_id)
        self.db.add(cart)
        await self.db.flush()
        return cart

    async def get_or_create(self, session_id: str) -> Cart:
        cart = await self.get_by_session(session_id)
        if not cart:
            cart = await self.create(session_id)
        return cart

    async def get_item(self, item_id: uuid.UUID) -> CartItem | None:
        result = await self.db.execute(
            select(CartItem)
            .where(CartItem.id == item_id)
            .options(selectinload(CartItem.product), selectinload(CartItem.cart))
        )
        return result.scalar_one_or_none()

    async def get_item_by_product(self, cart_id: uuid.UUID, product_id: uuid.UUID) -> CartItem | None:
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id,
            )
        )
        return result.scalar_one_or_none()

    async def add_item(self, cart_id: uuid.UUID, product_id: uuid.UUID, quantity: int) -> CartItem:
        existing = await self.get_item_by_product(cart_id, product_id)
        if existing:
            existing.quantity += quantity
            await self.db.flush()
            return existing

        item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
        self.db.add(item)
        await self.db.flush()
        return item

    async def update_item(self, item: CartItem, quantity: int) -> CartItem:
        item.quantity = quantity
        await self.db.flush()
        return item

    async def delete_item(self, item: CartItem) -> None:
        await self.db.delete(item)
        await self.db.flush()
