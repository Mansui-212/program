from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.admin.dependencies import get_current_admin
from app.db.session import get_db
from app.models.haki_record import HakiRecord
from app.models.user import User
from app.schemas.admin import AdminUserRead, HakiAdjustRequest, HakiRecordRead


router = APIRouter()


@router.get("", response_model=list[AdminUserRead])
def list_admin_users(
    keyword: str | None = Query(default=None, max_length=50),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    statement = select(User).order_by(User.created_at.asc(), User.id.asc())

    if keyword and keyword.strip():
        statement = statement.where(User.username.like(f"%{keyword.strip()}%"))

    return db.scalars(statement.offset(offset).limit(limit)).all()


@router.post("/{user_id}/haki", response_model=AdminUserRead)
def adjust_user_haki(
    user_id: int,
    data: HakiAdjustRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if data.change_value == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="哈气值调整不能为 0",
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    user.haki_value += data.change_value
    db.add(
        HakiRecord(
            user_id=user.id,
            change_value=data.change_value,
            reason=f"管理员 UID {admin.id} 调整：{data.reason.strip()}",
            action="admin_adjust",
            target_type="user",
            target_id=user.id,
            source_user_id=admin.id,
        )
    )
    db.commit()
    db.refresh(user)

    return user


@router.get("/{user_id}/haki-records", response_model=list[HakiRecordRead])
def list_user_haki_records(
    user_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if db.get(User, user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    statement = (
        select(HakiRecord)
        .where(HakiRecord.user_id == user_id)
        .order_by(HakiRecord.created_at.desc(), HakiRecord.id.desc())
        .limit(limit)
    )

    return db.scalars(statement).all()
