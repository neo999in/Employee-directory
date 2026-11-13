from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.exceptions import register_exception_handlers
from app.routers.employees import router as employees_router
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # create the employees table if it doesn't exist
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
app.include_router(employees_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "healthy"}
