import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.routers.employees import router as employees_router
from app.seed import seed_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("employee_api")

# Ensure tables are created
Base.metadata.create_all(bind=engine)
with SessionLocal() as db_session:
    seed_database(db_session)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database tables are created
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Checking seed data...")
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    # Shutdown logic if any
    logger.info("Application shutting down.")

app = FastAPI(
    title="Employee Directory API",
    description="High-performance Employee Directory Search API built with FastAPI and SQLAlchemy",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend access
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom validation exception handler for clean, friendly error messages
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        errors.append(f"{field}: {msg}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Request validation failed",
            "errors": errors
        }
    )

# Include Routers
app.include_router(employees_router, prefix="/api")

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Employee Directory API",
        "version": "1.0.0"
    }
