from fastapi import APIRouter

from app.api.v1.characters import router as characters_router
from app.api.v1.memes import router as memes_router
from app.api.v1.music_tracks import router as music_tracks_router
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
