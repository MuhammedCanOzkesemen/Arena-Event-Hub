import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

test_db_path = Path("test_arena_event_hub.db").resolve()
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path.as_posix()}"

from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if test_db_path.exists():
        try:
            test_db_path.unlink()
        except PermissionError:
            # Windows may keep the SQLite file locked briefly.
            pass


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
