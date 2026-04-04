from uuid import uuid4, UUID
from database import Base
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import UUID as SQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from datetime import UTC, datetime


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    arcana: Mapped[str] = mapped_column()  # Major or Minor
    suit: Mapped[str | None] = mapped_column()  # Cups, Swords, etc. (None for Major)
    meaning_upright: Mapped[str] = mapped_column()
    meaning_reversed: Mapped[str] = mapped_column()
    image_url: Mapped[str | None] = mapped_column()


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        SQL_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    image_file: Mapped[str | None] = mapped_column(
        String(200), nullable=True, default=None
    )
    entries: Mapped[list["Entry"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    # Store lowercase "email" value
    @validates("email")
    def lowercase_email(self, key, value):
        if value is not None:
            return value.strip().lower()
        return value


class Entry(Base):
    __tablename__ = "entries"

    id: Mapped[UUID] = mapped_column(
        SQL_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[UUID] = mapped_column(
        SQL_UUID(as_uuid=True),
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
