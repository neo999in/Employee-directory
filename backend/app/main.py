import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.exceptions import register_exception_handlers
from app.routers.employees import router as employees_router
from app.seed import seed_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("employee_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Ensuring database schema exists...")
    Base.metadata.create_all(bind=engine)
    if settings.SEED_ON_STARTUP:
        with SessionLocal() as db:
            seed_database(db)
    yield
    engine.dispose()
    logger.info("Application shut down; connection pool disposed.")


app = FastAPI(
    title="Employee Directory API",
    description="Employee Directory Search API built with FastAPI, SQLAlchemy and MySQL",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(employees_router, prefix="/api")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "Employee Directory API", "version": "1.0.0"}
