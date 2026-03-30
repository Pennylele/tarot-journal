from database import Base
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import UTC, datetime


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    arcana: Mapped[str] = mapped_column()  # Major or Minor
    suit: Mapped[str | None] = mapped_column()  # Cups, Swords, etc. (None for Major)
    meaning_upright: Mapped[str] = mapped_column()
    meaning_reversed: Mapped[str] = mapped_column()
    image_url: Mapped[str | None] = mapped_column()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    entries: Mapped[list["Entry"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    # will add password and image_file later


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"), nullable=False)

    author: Mapped[User] = relationship(back_populates="entries")

    card: Mapped["Card"] = relationship()
