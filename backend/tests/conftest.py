import os
import tempfile

import pytest

# Point the app at a throwaway SQLite DB *before* app modules are imported,
# so tests never touch a real MySQL instance.
_tmp_dir = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_tmp_dir, 'test.db')}"
os.environ["CORS_ORIGINS"] = "http://testserver"
os.environ["SEED_ON_STARTUP"] = "true"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    # Context manager runs the lifespan (schema creation + seed).
    with TestClient(app) as test_client:
        yield test_client
