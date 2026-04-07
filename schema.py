from pydantic import BaseModel, ConfigDict, Field, EmailStr, BeforeValidator
from datetime import datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID


class ArcanaType(StrEnum):
    MAJOR = "major"
    MINOR = "minor"


class SuitType(StrEnum):
    SWORDS = "swords"
    CUPS = "cups"
    WANDS = "wands"
    PENTACLES = "pentacles"


# Helper to make string inputs case-insensitive before matching Enums
def to_lower(v: object) -> object:
    if isinstance(v, str):
        return v.lower()
    return v


# Annotated types that pre-process the input string to lowercase
CaseInsensitiveArcana = Annotated[ArcanaType, BeforeValidator(to_lower)]
CaseInsensitiveSuit = Annotated[SuitType, BeforeValidator(to_lower)]


# For User input validation
class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)


# For User output validation
class UserPublic(BaseModel):
    # from_attributes=True allows Pydantic to read data from SQLAlchemy model objects
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str


class UserPrivate(UserPublic):
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


# For Card input validation
class CardBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120)
    arcana: CaseInsensitiveArcana | None = Field(default=None)
    suit: CaseInsensitiveSuit | None = Field(default=None)
    meaning_upright: str = Field(min_length=1, max_length=1000)
    meaning_reversed: str = Field(min_length=1, max_length=1000)
    image_url: str | None = Field(default=None)


class CardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    arcana: CaseInsensitiveArcana | None = Field(default=None)
    suit: CaseInsensitiveSuit | None = Field(default=None)
    meaning_upright: str | None = Field(default=None, min_length=1, max_length=1000)
    meaning_reversed: str | None = Field(default=None, min_length=1, max_length=1000)
    image_url: str | None = Field(default=None, min_length=1, max_length=100)


# For Card output validation
class CardResponse(CardBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# For Entry input validation
class EntryBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class EntryCreate(EntryBase):
    card_id: int


class EntryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)


# For Entry output validation
class EntryResponse(EntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    card_id: int
    date_posted: datetime
