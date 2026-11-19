import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine, ensure_fulltext_index
from app.core.exceptions import register_exception_handlers
from app.routers.employees import router as employees_router
from app.routers.health import router as health_router
from app.seed import seed_database

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Retry database connection on startup to handle cold starts (e.g. Docker initialization)
    max_retries = 10
    retry_delay = 2
    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)  # create the employees table if it doesn't exist
            ensure_fulltext_index()  # upgrade tables created before the FULLTEXT index existed
            break
        except OperationalError as exc:
            if attempt == max_retries:
                logger.error(f"Failed to connect to database after {max_retries} attempts.")
                raise
            logger.warning(
                f"Database not ready (attempt {attempt}/{max_retries}): {exc}. Retrying in {retry_delay}s..."
            )
            time.sleep(retry_delay)

    if settings.SEED_ON_STARTUP:
        with SessionLocal() as db:
            seed_database(db)
    yield
    engine.dispose()


app = FastAPI(title="Employee Directory API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["GET"],
    allow_headers=["*"],
)
register_exception_handlers(app)
app.include_router(health_router)
app.include_router(employees_router, prefix="/api")

