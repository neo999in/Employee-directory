"""
Database connection.

Why this approach (SQLAlchemy engine + connection pool + one session per request):
- Pool: connections are reused instead of reconnecting on every request, and the
  pool size caps how many connections we open, so MySQL is never overloaded.
- pool_pre_ping / pool_recycle: dead or stale connections are replaced automatically.
- get_db(): every request gets its own session, which is always closed afterwards.
- ORM queries are parameterized, so user input can't cause SQL injection.
- Credentials come only from DATABASE_URL (env var), never from code.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite is only used by the tests.
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_recycle=settings.DB_POOL_RECYCLE_SECONDS,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_fulltext_index() -> None:
    """create_all() never alters an existing table, so add the FULLTEXT index to older MySQL databases."""
    if engine.dialect.name != "mysql":
        return
    from app.models.employee import FULLTEXT_INDEX_NAME

    with engine.begin() as conn:
        exists = conn.execute(
            text(
                "SELECT 1 FROM information_schema.statistics WHERE table_schema = DATABASE() "
                "AND table_name = 'employees' AND index_name = :n LIMIT 1"
            ),
            {"n": FULLTEXT_INDEX_NAME},
        ).first()
        if not exists:
            conn.execute(text(f"ALTER TABLE employees ADD FULLTEXT INDEX {FULLTEXT_INDEX_NAME} (name, department)"))
