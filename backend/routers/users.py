from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from schema import (
    UserPublic,
    UserPrivate,
    UserUpdate,
    UserCreate,
    Token,
    EntryResponse,
)
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User, Entry
from auth import (
    CurrentUser,
    hash_password,
    verify_password,
    create_access_token,
)
from config import settings
from datetime import timedelta

router = APIRouter()


@router.post("", response_model=UserPublic)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], user: UserCreate):
    result = await db.execute(select(User).where(User.email == user.email.lower()))
    existing_email = result.scalars().one_or_none()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    result = await db.execute(select(User).where(User.username == user.username))
    existing_user = result.scalars().one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    result = await db.execute(
        select(User).where(User.email == form_data.username.lower())
    )
    user = result.scalars().one_or_none()
    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserPrivate)
async def get_current_user(
    current_user: CurrentUser,
):
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: UUID, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get("/{user_id}/entries", response_model=list[EntryResponse])
async def get_user_entries(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    # Ensure users can only query their own entry list via this endpoint
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these entries",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = await db.execute(
        select(Entry).where(Entry.author == user).order_by(Entry.date_posted.desc())
    )

    entries = result.scalars().all()
    return entries


@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user_update.username is not None and user_update.username != user.username:
        result = await db.execute(
            select(User).where(User.username == user_update.username)
        )
        existing_username = result.scalars().one_or_none()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

    if user_update.email is not None and user_update.email != user.email.lower():
        result = await db.execute(
            select(User).where(User.email == user_update.email.lower())
        )
        existing_email = result.scalars().one_or_none()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.delete(user)
    await db.commit()
