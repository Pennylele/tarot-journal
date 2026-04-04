from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import Base, engine, get_db
import logging
import models
from routers import cards, entries, users

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("tarot_journal")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # This starts a database transaction.
    async with engine.begin() as conn:
        logger.info("--- Initializing Database Tables ---")
        await conn.run_sync(Base.metadata.create_all)
    yield
    logger.info("--- Shutting Down Database Connection ---")
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(cards.router, prefix="/api/cards", tags=["cards"])
app.include_router(entries.router, prefix="/api/entries", tags=["entries"])
app.include_router(users.router, prefix="/api/users", tags=["users"])


@app.get("/")
def read_root():
    return "Tarot Journal App - FastAPI"
