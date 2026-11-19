import os
import tempfile

import pytest

# Point the app at a throwaway SQLite DB *before* app modules are imported,
# so tests never touch a real MySQL instance.
# Set MYSQL_TEST_URL (see docker-compose.test.yml) to run the same tests against real MySQL,
# which is the only way to exercise the FULLTEXT queries.
_tmp_dir = tempfile.mkdtemp()
USING_MYSQL = bool(os.environ.get("MYSQL_TEST_URL"))
os.environ["DATABASE_URL"] = os.environ.get("MYSQL_TEST_URL") or f"sqlite:///{os.path.join(_tmp_dir, 'test.db')}"
os.environ["CORS_ORIGINS"] = "http://testserver"
os.environ["SEED_ON_STARTUP"] = "true"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    if USING_MYSQL:
        from app.core.database import Base, engine

        Base.metadata.drop_all(bind=engine)  # start from an empty schema every run
    # Context manager runs the lifespan (schema creation + seed).
    with TestClient(app) as test_client:
        yield test_client
