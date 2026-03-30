from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime


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

    id: int
    username: str


class UserPrivate(UserPublic):
    email: EmailStr


# For Card input validation
class CardBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    arcana: str = Field(min_length=1, max_length=20)
    suit: str | None = Field(
        default=None, min_length=1, max_length=100
    )  # Cups, Swords, etc. (None for Major)
    meaning_upright: str = Field(min_length=1, max_length=1000)
    meaning_reversed: str = Field(min_length=1, max_length=1000)
    image_url: str | None = Field(default=None)


class CardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    arcana: str | None = Field(default=None, max_length=20)
    suit: str | None = Field(
        default=None, min_length=1, max_length=100
    )  # Cups, Swords, etc. (None for Major)
    meaning_upright: str | None = Field(default=None, min_length=1, max_length=1000)
    meaning_reversed: str | None = Field(default=None, min_length=1, max_length=1000)
    image_url: str | None = Field(default=None, min_length=1, max_length=100)


# For Card output validation
class CardResponse(CardBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str


# For Entry input validation
class EntryBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class EntryCreate(EntryBase):
    user_id: int
    card_id: int


class EntryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)


# For Entry output validation
class EntryResponse(EntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    card_id: int
    date_posted: datetime
