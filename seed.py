# Seeding Script to populate data into the database.
import json
import asyncio
import sys
from sqlalchemy import select, func, delete
from database import AsyncSessionLocal, engine
from models import Card


async def seed_data(reset: bool = False):
    with open("card_data.json", "r") as f:
        cards_data = json.load(f)

    async with AsyncSessionLocal() as session:
        # starts this "All or Nothing" period. It automatically handles commit, rollback, and resource management.
        async with session.begin():
            if reset:
                print("Reset flag detected. Clearing existing cards...")
                await session.execute(delete(Card))
                # Note: This clears rows but doesn't reset the ID sequence in all DBs.
                # For a full reset, TRUNCATE is better but delete() is more cross-compatible.

            # Check if cards already exist
            result = await session.execute(select(func.count()).select_from(Card))
            count = result.scalar()

            if count is not None and count > 0:
                print(f"Database already contains {count} cards. Skipping seed.")
                return

            for card_dict in cards_data:
                # Generate slug from name: "The Fool" -> "the-fool"
                card_dict["slug"] = card_dict["name"].lower().replace(" ", "-")
                new_card = Card(**card_dict)
                session.add(new_card)

            print(f"Successfully seeded {len(cards_data)} cards into PostgreSQL!")

    await engine.dispose()


if __name__ == "__main__":
    # Check if "--reset" was passed in the command line
    do_reset = "--reset" in sys.argv
    asyncio.run(seed_data(reset=do_reset))
