"""
Database engine and session management.

Why this approach:
- SQLAlchemy engine with a connection pool: connections are opened once and
  reused across requests instead of paying a TCP + auth handshake per request,
  and the pool size caps how many connections the app can open, so a traffic
  spike can't exhaust MySQL's max_connections.
- pool_pre_ping: checks a connection before handing it out, so connections
  dropped by MySQL's wait_timeout / network blips are replaced transparently
  instead of failing the request.
- pool_recycle: proactively replaces connections before MySQL's idle timeout.
- One session per request (get_db dependency): each request gets an isolated
  unit of work that is always closed (connection returned to pool) even if the
  request raises.
- Parameterized queries via the ORM: user input is never concatenated into
  SQL, which prevents SQL injection.
- Credentials live only in DATABASE_URL (env var), never in code.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

connect_args = {}
engine_kwargs = {}

if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite is only used for local tests; it needs this flag because
    # FastAPI may use the connection from a different thread.
    connect_args["check_same_thread"] = False
else:
    engine_kwargs.update(
        pool_pre_ping=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_recycle=settings.DB_POOL_RECYCLE_SECONDS,
    )

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
