import uuid
from decimal import Decimal

from sqlalchemy import String, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String(255), index=True)

    description: Mapped[str | None] = mapped_column(Text)

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        index=True
    )

    image: Mapped[str | None] = mapped_column(String(500))

    category: Mapped[str] = mapped_column(
        String(100),
        index=True
    )
