from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import Token, UserLogin, UserOut, UserRegister
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegister,
    service: AuthService = Depends(get_auth_service),
) -> UserOut:
    return await service.register(payload)


@router.post("/login", response_model=Token)
async def login(
    payload: UserLogin,
    service: AuthService = Depends(get_auth_service),
) -> Token:
    return await service.login(payload)


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)
