# Seeding Script to populate data into the database.
import json
import asyncio
from sqlalchemy import select, func
from database import AsyncSessionLocal, engine
from models import Card


async def seed_data():
    with open("card_data.json", "r") as f:
        cards_data = json.load(f)

    async with AsyncSessionLocal() as session:
        # starts this "All or Nothing" period. It automatically handles commit, rollback, and resource management.
        async with session.begin():
            # Check if cards already exist
            result = await session.execute(select(func.count()).select_from(Card))
            count = result.scalar()

            if count is not None and count > 0:
                print(f"Database already contains {count} cards. Skipping seed.")
                return

            for card_dict in cards_data:
                new_card = Card(**card_dict)
                session.add(new_card)

            print(f"Successfully seeded {len(cards_data)} cards into PostgreSQL!")


if __name__ == "__main__":
    asyncio.run(seed_data())
