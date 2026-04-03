from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.cart_repo import CartRepository
from app.repositories.user_repo import UserRepository
from app.schemas.user import Token, UserLogin, UserOut, UserRegister


class AuthService:
    def __init__(self, user_repo: UserRepository, cart_repo: CartRepository) -> None:
        self.user_repo = user_repo
        self.cart_repo = cart_repo

    async def register(self, payload: UserRegister) -> UserOut:
        existing = await self.user_repo.get_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        user = await self.user_repo.create(
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )
        return UserOut.model_validate(user)

    async def login(self, payload: UserLogin, session_id: str | None = None) -> Token:
        user = await self.user_repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

        if session_id:
            await self.cart_repo.merge_session_into_user(session_id, user.id)

        return Token(access_token=create_access_token(user.id))
