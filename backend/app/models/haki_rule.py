from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HakiRule(Base):
    __tablename__ = "haki_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
