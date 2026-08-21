from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.haki_record import HakiRecord
from app.models.haki_rule import HakiRule
from app.models.user import User


DEFAULT_HAKI_RULES = {
    "upload_meme": 10,
    "upload_music": 10,
    "favorite_get": 5,
    "download_get": 1,
    "admin_pick": 50,
}

ACTION_REASONS = {
    "upload_meme": "发布表情包",
    "upload_music": "发布音乐",
    "favorite_get": "作品被收藏",
    "download_get": "作品被下载",
    "admin_pick": "作品被管理员精选",
}


def get_haki_rule_value(db: Session, action: str) -> int:
    value = db.scalar(select(HakiRule.value).where(HakiRule.action == action))
    return value if value is not None else DEFAULT_HAKI_RULES.get(action, 0)


def add_haki(
    db: Session,
    user: User,
    action: str,
    *,
    target_type: str | None = None,
    target_id: int | None = None,
    source_user_id: int | None = None,
    reason: str | None = None,
) -> HakiRecord | None:
    value = get_haki_rule_value(db, action)

    if value == 0:
        return None

    user.haki_value += value
    record = HakiRecord(
        user_id=user.id,
        change_value=value,
        reason=reason or ACTION_REASONS.get(action, action),
        action=action,
        target_type=target_type,
        target_id=target_id,
        source_user_id=source_user_id,
    )
    db.add(record)
    return record
