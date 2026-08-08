"""
Pytest configuration and fixtures for Flare backend tests.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from app.database import Base, get_db, engine
from app.models_db import User
from app.auth import hash_password, create_access_token


@pytest.fixture(autouse=True)
def setup_db():
    """Create fresh tables for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    from app.database import SessionLocal
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def admin_user(db_session):
    user = User(
        email="admin@test.com",
        name="Test Admin",
        hashed_password=hash_password("admin123"),
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def analyst_user(db_session):
    user = User(
        email="analyst@test.com",
        name="Test Analyst",
        hashed_password=hash_password("analyst123"),
        role="analyst",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def viewer_user(db_session):
    user = User(
        email="viewer@test.com",
        name="Test Viewer",
        hashed_password=hash_password("viewer123"),
        role="viewer",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    return create_access_token({"sub": admin_user.id})


@pytest.fixture
def analyst_token(analyst_user):
    return create_access_token({"sub": analyst_user.id})


@pytest.fixture
def viewer_token(viewer_user):
    return create_access_token({"sub": viewer_user.id})


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def analyst_headers(analyst_token):
    return {"Authorization": f"Bearer {analyst_token}"}


@pytest.fixture
def viewer_headers(viewer_token):
    return {"Authorization": f"Bearer {viewer_token}"}
