from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base


class Anecdote(Base):
    content: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    report_count: Mapped[int] = mapped_column(default=0)

    user: Mapped["User"] = relationship(
        "User", back_populates="anecdotes", lazy="selectin"
    )
    rates: Mapped[list["Rate"]] = relationship(
        "Rate", back_populates="anecdote", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Anecdote(id={self.id}, content='{self.content}')>"


class Rate(Base):
    anecdote_id: Mapped[int] = mapped_column(
        ForeignKey("anecdotes.id"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    rating: Mapped[int | None]

    anecdote: Mapped["Anecdote"] = relationship("Anecdote", back_populates="rates")

    user: Mapped["User"] = relationship("User", back_populates="rates")

    def __repr__(self):
        return f"<Rate(anecdote_id={self.anecdote_id}, user_id={self.user_id}, rating={self.rating})>"
