# tests/test_auth.py
"""
Tests for auth.py

These tests verify:
- Users can sign up
- Users can sign in
- JWT tokens are created and validated
- /me returns the correct user
"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from app.main import app
from app.models import Base
from app.db import get_db

import tempfile, atexit
import os


# Create a unique temporary database file for THIS test file
tmp_db = tempfile.NamedTemporaryFile(delete=False)
db_url = f"sqlite:///{tmp_db.name}"

db_path = tmp_db.name
# ensure file is deleted when tests finish
atexit.register(lambda: os.remove(db_path))

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False},
    future=True
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base.metadata.create_all(bind=engine)


# Override get_db() so tests use the test DB, not real DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# -------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------
def test_signup():
    response = client.post("/auth/signup", params={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data


def test_signin():
    # first sign up a user
    client.post("/auth/signup", params={
        "email": "login@example.com",
        "password": "abc123"
    })

    # now sign in
    response = client.post("/auth/signin", params={
        "email": "login@example.com",
        "password": "abc123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_me_endpoint():
    # create and login
    client.post("/auth/signup", params={
        "email": "me@example.com",
        "password": "zzz"
    })
    login = client.post("/auth/signin", params={
        "email": "me@example.com",
        "password": "zzz"
    }).json()

    token = login["access_token"]

    # call /me with Authorization header
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
