from typing import TYPE_CHECKING
from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base


class User(Base):
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]

    anecdotes: Mapped[list["Anecdote"]] = relationship(
        "Anecdote", back_populates="user", cascade="all, delete-orphan"
    )
    rates: Mapped[list["Rate"]] = relationship(
        "Rate", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"
