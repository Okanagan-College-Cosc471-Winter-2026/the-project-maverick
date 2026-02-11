from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.db import SessionLocal
from app.api.deps import get_db


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Creates a fresh database session for a test.
    We're not using a separate test DB or transaction rollback here 
    to keep it compatible with the existing dev DB setup as requested.
    But we yield a session that tests can use.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Test client that uses the override DB session.
    """
    # Override the get_db dependency to use our test session
    app.dependency_overrides[get_db] = lambda: db
    
    with TestClient(app) as c:
        yield c
        
    # Clear overrides after test
    app.dependency_overrides.clear()
