from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database.database import Base


class Gift(Base):
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    gift_id: Mapped[str]
    text: Mapped[str | None]
    telegram_payment_charge_id: Mapped[str]


class Donation(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int]
    telegram_payment_charge_id: Mapped[str]
