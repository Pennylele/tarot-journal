from fastapi import APIRouter, Depends, HTTPException, status
from schema import EntryResponse, EntryCreate, EntryUpdate
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Entry, Card
from database import get_db
from uuid import UUID
from auth import CurrentUser


router = APIRouter()


@router.get("", response_model=list[EntryResponse])
async def list_entries(
    db: Annotated[AsyncSession, Depends(get_db)], current_user: CurrentUser
):
    # Only return entries belonging to the current user
    results = await db.execute(
        select(Entry)
        .where(Entry.user_id == current_user.id)
        .order_by(Entry.date_posted.desc())
    )
    entries = results.scalars().all()
    return entries


@router.get("/{entry_id}", response_model=EntryResponse)
async def get_entry(
    db: Annotated[AsyncSession, Depends(get_db)],
    entry_id: UUID,
    current_user: CurrentUser,
):
    results = await db.execute(select(Entry).where(Entry.id == entry_id))
    entry = results.scalars().one_or_none()

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        )

    # Authorization check
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this entry",
        )

    return entry


@router.post("", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
async def create_entry(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    entry: EntryCreate,
):
    # Validate card exists
    card_result = await db.execute(select(Card).where(Card.id == entry.card_id))
    if card_result.scalars().one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid card ID"
        )

    new_entry = Entry(
        title=entry.title,
        content=entry.content,
        user_id=current_user.id,
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
    current_user: CurrentUser,
):
    result = await db.execute(select(Entry).where(Entry.id == entry_id))
    entry = result.scalars().one_or_none()
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        )

    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
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
    entry.card_id = entry_data.card_id

    await db.commit()
    await db.refresh(entry, attribute_names=["author"])
    return entry


@router.patch("/{entry_id}", response_model=EntryResponse)
async def update_entry_partial(
    db: Annotated[AsyncSession, Depends(get_db)],
    entry_data: EntryUpdate,
    entry_id: UUID,
    current_user: CurrentUser,
):
    result = await db.execute(select(Entry).where(Entry.id == entry_id))
    entry = result.scalars().one_or_none()
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        )

    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this entry",
        )

    update_data = entry_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entry, key, value)

    await db.commit()
    await db.refresh(entry, attribute_names=["author"])
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    db: Annotated[AsyncSession, Depends(get_db)],
    entry_id: UUID,
    current_user: CurrentUser,
):
    result = await db.execute(select(Entry).where(Entry.id == entry_id))
    entry = result.scalars().one_or_none()
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found"
        )

    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this entry",
        )

    await db.delete(entry)
    await db.commit()
