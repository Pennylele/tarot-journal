from fastapi import APIRouter, Depends, Query, HTTPException, status
from schema import EntryResponse, EntryCreate, EntryUpdate, ArcanaType, SuitType
from typing import Annotated, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models import Entry, User, Card
from database import get_db
from models import Entry, User
from uuid import UUID


router = APIRouter()


# Need to implement Authorization logic later. Right now the APIs are returning all values.
@router.get("", response_model=list[EntryResponse])
async def list_entries(db: Annotated[AsyncSession, Depends(get_db)]):
    results = await db.execute(select(Entry).order_by(Entry.date_posted.desc()))
    entries = results.scalars().all()
    return entries


@router.get("/{entry_id}", response_model=EntryResponse)
async def get_entry(db: Annotated[AsyncSession, Depends(get_db)], entry_id: UUID):
    results = await db.execute(select(Entry).where(Entry.id == entry_id))
    entry = results.scalars().one_or_none()
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        )
    return entry


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_entry(
    db: Annotated[AsyncSession, Depends(get_db)], entry: EntryCreate
):
    # Verify User exists
    user_result = await db.execute(select(User).where(User.id == entry.user_id))
    user = user_result.scalars().one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Verify Card exists
    card_result = await db.execute(select(Card).where(Card.id == entry.card_id))
    card = card_result.scalars().one_or_none()
    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )

    new_entry = Entry(
        title=entry.title,
        content=entry.content,
        user_id=entry.user_id,
        card_id=entry.card_id,
    )

    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry, attribute_names=["author"])
    return new_entry


@router.put("/{entry_id}", response_model=EntryResponse)
async def update_entry_full(
    db: Annotated[AsyncSession, Depends(get_db)],
    entry_data: EntryCreate,
    entry_id: UUID,
):
    result = await db.execute(select(Entry).where(Entry.id == entry_id))
    entry = result.scalars().one_or_none()
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        )

    if entry_data.user_id != entry.user_id:
        result = await db.execute(select(User).where(User.id == entry_data.user_id))
        user = result.scalars().one_or_none()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    if entry_data.card_id != entry.card_id:
        card_result = await db.execute(
            select(Card).where(Card.id == entry_data.card_id)
        )
        card = card_result.scalars().one_or_none()
        if card is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
            )

    entry.title = entry_data.title
    entry.content = entry_data.content
    entry.user_id = entry_data.user_id
    entry.card_id = entry_data.card_id

    await db.commit()
    await db.refresh(entry, attribute_names=["author"])
    return entry


@router.patch("/{entry_id}", response_model=EntryResponse)
async def update_entry_partial(
    db: Annotated[AsyncSession, Depends(get_db)],
    entry_data: EntryUpdate,
    entry_id: UUID,
):
    result = await db.execute(select(Entry).where(Entry.id == entry_id))
    entry = result.scalars().one_or_none()
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        )

    update_data = entry_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entry, key, value)

    await db.commit()
    await db.refresh(entry, attribute_names=["author"])
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(db: Annotated[AsyncSession, Depends(get_db)], entry_id: UUID):
    result = await db.execute(select(Entry).where(Entry.id == entry_id))
    entry = result.scalars().one_or_none()
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        )

    await db.delete(entry)
    await db.commit()
