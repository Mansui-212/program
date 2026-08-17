from fastapi import Depends

from app.api.v1.auth import get_current_user
from app.core.permissions import require_admin
from app.models.user import User


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    return require_admin(current_user)
