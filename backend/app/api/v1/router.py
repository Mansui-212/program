from fastapi import APIRouter

from app.api.v1.admin.router import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.characters import router as characters_router
from app.api.v1.chronicle import router as chronicle_router
from app.api.v1.memes import router as memes_router
from app.api.v1.music_tracks import router as music_tracks_router
from app.api.v1.search import router as search_router
from app.api.v1.submissions import router as submissions_router
from app.api.v1.system import router as system_router
from app.api.v1.users import router as users_router


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

api_router.include_router(
    chronicle_router,
    prefix="/chronicle",
    tags=["chronicle"],
)

api_router.include_router(
    memes_router,
    prefix="/memes",
    tags=["memes"],
)

api_router.include_router(
    music_tracks_router,
    prefix="/music-tracks",
    tags=["music-tracks"],
)

api_router.include_router(
    search_router,
    prefix="/search",
    tags=["search"],
)

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"],
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["users"],
)

api_router.include_router(
    submissions_router,
    prefix="/submissions",
    tags=["submissions"],
)

api_router.include_router(
    admin_router,
    prefix="/admin",
    tags=["admin"],
)
