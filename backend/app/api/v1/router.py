from fastapi import APIRouter

from app.api.v1.characters import router as characters_router
from app.api.v1.system import router as system_router


api_router = APIRouter()

api_router.include_router(
    system_router,
    prefix="/system",
    tags=["system"],
)

api_router.include_router(
    characters_router,
    prefix="/characters",
    tags=["characters"],
)
