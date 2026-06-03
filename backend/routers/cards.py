from fastapi import APIRouter, Depends, Query, HTTPException, status
from schema import CardResponse, CardUpdate, ArcanaType, SuitType
from typing import Annotated, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from database import get_db
from models import Card

router = APIRouter()


# GET /api/cards/
# GET /api/cards/?arcana=Major
# GET /api/cards/?arcana=Minor&suit=Swords
@router.get("", response_model=list[CardResponse])
async def list_cards(
    db: Annotated[AsyncSession, Depends(get_db)],
    arcana: Optional[ArcanaType] = Query(None, description="Filter by Major or Minor"),
    suit: Optional[SuitType] = Query(None, description="Filter by suit"),
):
    """
    List a set of cards.
    """
    query = select(Card)
    if arcana:
        query = query.where(func.lower(Card.arcana) == arcana.lower())
    if suit:
        query = query.where(func.lower(Card.suit) == suit.lower())

    result = await db.execute(query)
    return result.scalars().all()


# Get a random card
@router.get("/random", response_model=CardResponse)
async def get_random_card(db: Annotated[AsyncSession, Depends(get_db)]):
    query = select(Card).order_by(func.random()).limit(1)
    result = await db.execute(query)
    card = result.scalars().unique().one_or_none()

    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No cards found in the database",
        )

    return card


# get a specific card - to check for its meanings I guess
@router.get("/{card_identifier}", response_model=CardResponse)
async def get_card(db: Annotated[AsyncSession, Depends(get_db)], card_identifier: str):
    """
    Fetch a specific card by its numeric ID OR its exact name.
    """
    if card_identifier.isdigit():
        query = select(Card).where(Card.id == int(card_identifier))
    else:
        query = select(Card).where(
            Card.slug == card_identifier.lower().replace(" ", "-")
        )

    result = await db.execute(query)
    card = result.scalars().one_or_none()

    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card with identifier '{card_identifier}' not found",
        )

    return card
