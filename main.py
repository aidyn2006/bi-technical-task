from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth_router import router as auth_router
from app.api.cart_router import router as cart_router
from app.api.product_router import router as product_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(product_router, prefix=settings.API_PREFIX)
app.include_router(cart_router, prefix=settings.API_PREFIX)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
