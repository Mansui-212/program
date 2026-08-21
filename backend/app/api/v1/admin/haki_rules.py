from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.admin.dependencies import get_current_admin
from app.db.session import get_db
from app.models.haki_rule import HakiRule
from app.models.user import User
from app.schemas.haki_rule import HakiRuleRead, HakiRuleUpdate
from app.services.haki import DEFAULT_HAKI_RULES


router = APIRouter()


@router.get("", response_model=list[HakiRuleRead])
def list_haki_rules(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return db.scalars(select(HakiRule).order_by(HakiRule.id.asc())).all()


@router.put("/{action}", response_model=HakiRuleRead)
def update_haki_rule(
    action: str,
    data: HakiRuleUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if action not in DEFAULT_HAKI_RULES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="哈气规则不存在")

    rule = db.scalar(select(HakiRule).where(HakiRule.action == action))
    if rule is None:
        rule = HakiRule(action=action, value=data.value)
        db.add(rule)
    else:
        rule.value = data.value

    db.commit()
    db.refresh(rule)
    return rule
