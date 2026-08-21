from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.favorite import Favorite
from app.models.haki_record import HakiRecord
from app.models.meme import Meme
from app.models.music_track import MusicTrack
from app.models.user import User
from app.schemas.favorite import FavoriteCreate, FavoriteRead, FavoriteStatusRead
from app.services.haki import add_haki


router = APIRouter()


def get_target(db: Session, target_type: str, target_id: int) -> Meme | MusicTrack:
    target = db.get(Meme, target_id) if target_type == "meme" else db.get(MusicTrack, target_id)
    if target is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏内容不存在")
    return target


def serialize_favorite(favorite: Favorite, target: Meme | MusicTrack) -> FavoriteRead:
    if isinstance(target, Meme):
        return FavoriteRead(
            id=favorite.id,
            target_type="meme",
            target_id=target.id,
            title=target.title,
            description=target.description,
            image_url=target.image_url,
            author_name=target.author_name,
            created_at=favorite.created_at,
        )

    return FavoriteRead(
        id=favorite.id,
        target_type="music",
        target_id=target.id,
        title=target.title,
        description=target.description,
        audio_url=target.audio_url,
        cover_url=target.cover_url,
        author_name=target.author_name,
        created_at=favorite.created_at,
    )


@router.post("", response_model=FavoriteStatusRead, status_code=status.HTTP_201_CREATED)
def create_favorite(
    data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target = get_target(db, data.target_type, data.target_id)

    if target.author_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能收藏自己的作品")

    exists = db.scalar(
        select(Favorite.id).where(
            Favorite.user_id == current_user.id,
            Favorite.target_type == data.target_type,
            Favorite.target_id == data.target_id,
        )
    )
    if exists is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="已经收藏过该内容")

    db.add(Favorite(user_id=current_user.id, target_type=data.target_type, target_id=data.target_id))

    if target.author_id is not None:
        rewarded = db.scalar(
            select(HakiRecord.id).where(
                HakiRecord.user_id == target.author_id,
                HakiRecord.action == "favorite_get",
                HakiRecord.target_type == data.target_type,
                HakiRecord.target_id == target.id,
                HakiRecord.source_user_id == current_user.id,
            )
        )
        author = db.get(User, target.author_id)
        if rewarded is None and author is not None:
            add_haki(
                db,
                author,
                "favorite_get",
                target_type=data.target_type,
                target_id=target.id,
                source_user_id=current_user.id,
            )

    db.commit()
    return FavoriteStatusRead(
        target_type=data.target_type,
        target_id=data.target_id,
        is_favorited=True,
    )


@router.delete("/{target_type}/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(
    target_type: str,
    target_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    if target_type not in {"meme", "music"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="收藏类型无效")

    favorite = db.scalar(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.target_type == target_type,
            Favorite.target_id == target_id,
        )
    )
    if favorite is not None:
        db.delete(favorite)
        db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=list[FavoriteRead])
def list_my_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    favorites = db.scalars(
        select(Favorite)
        .where(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc(), Favorite.id.desc())
    ).all()

    meme_ids = [favorite.target_id for favorite in favorites if favorite.target_type == "meme"]
    music_ids = [favorite.target_id for favorite in favorites if favorite.target_type == "music"]
    memes = {item.id: item for item in db.scalars(select(Meme).where(Meme.id.in_(meme_ids))).all()} if meme_ids else {}
    tracks = {item.id: item for item in db.scalars(select(MusicTrack).where(MusicTrack.id.in_(music_ids))).all()} if music_ids else {}

    items: list[FavoriteRead] = []
    for favorite in favorites:
        target = memes.get(favorite.target_id) if favorite.target_type == "meme" else tracks.get(favorite.target_id)
        if target is not None:
            items.append(serialize_favorite(favorite, target))

    return items


@router.get("/me/{target_type}/{target_id}", response_model=FavoriteStatusRead)
def get_favorite_status(
    target_type: str,
    target_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if target_type not in {"meme", "music"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="收藏类型无效")

    is_favorited = db.scalar(
        select(Favorite.id).where(
            Favorite.user_id == current_user.id,
            Favorite.target_type == target_type,
            Favorite.target_id == target_id,
        )
    ) is not None
    return FavoriteStatusRead(target_type=target_type, target_id=target_id, is_favorited=is_favorited)
