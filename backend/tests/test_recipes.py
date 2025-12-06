# tests/test_recipes.py
"""
===============================================================================
Tests for recipes.py

These tests verify:
- Extracting a recipe from a URL (downloader + Gemini are mocked)
- Recipes and ingredients are saved correctly
- Listing, retrieving, and deleting recipes works

These tests DO NOT:
- Hit actual downloader
- Hit actual Gemini
- Use real authentication
- Touch the production DB

Everything is fully isolated using an in-memory SQLite test database.
===============================================================================
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import get_db
from app.models import Base, User, Recipe, RecipeIngredient


# ==============================================================================
# FIXTURE: Create a fresh in-memory SQLite DB for this test module
# ==============================================================================
@pytest.fixture(scope="module")
def test_db():
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite://",      # <-- not sqlite:///:memory:
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True
    )

    Base.metadata.create_all(bind=engine)

    # override get_db
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    return TestingSessionLocal


# ==============================================================================
# FIXTURE: FastAPI TestClient that uses the isolated DB
# ==============================================================================
@pytest.fixture
def client(test_db):
    return TestClient(app)


# ==============================================================================
# Helper: Create a fresh user + override get_current_user
# ==============================================================================
def create_test_user(SessionLocal, email):
    """
    Creates a new user in the test DB and returns it.
    Also overrides get_current_user so all recipe endpoints use this user.
    """

    db = SessionLocal()
    user = User(email=email, password_hash="pw")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    # Override get_current_user so routes use THIS user
    from app.auth import get_current_user
    def fake_user_dep():
        return user
    app.dependency_overrides[get_current_user] = fake_user_dep

    return user


# ==============================================================================
# TEST 1 — Extract recipe (happy path)
# ==============================================================================
@patch("app.recipes.extract_recipe")
@patch("app.recipes.download_audio")
def test_extract_recipe_endpoint(mock_dl, mock_gem, client, test_db):
    # Create a specific user for this test
    user = create_test_user(test_db, "extract_test@example.com")

    # Mock download_audio to return a temp audio file
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "audio.mp3")
    with open(audio_path, "wb") as f:
        f.write(b"fake audio bytes")
    mock_dl.return_value = audio_path

    # Mock Gemini recipe extraction
    mock_gem.return_value = {
        "title": "Test Pasta",
        "ingredients": ["pasta", "salt"],
        "instructions": "Boil pasta."
    }

    # Call the endpoint
    response = client.post("/recipes/extract", params={"url": "https://x.com/video"})
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Test Pasta"
    assert data["ingredients"] == ["pasta", "salt"]
    assert "Boil pasta" in data["instructions"]


# ==============================================================================
# TEST 2 — CRUD operations
# ==============================================================================
def test_recipe_crud(client, test_db):
    user = create_test_user(test_db, "crud_test@example.com")

    # Insert a recipe manually using DB session
    db = test_db()
    recipe = Recipe(
        user_id=user.id,
        title="Toast",
        instructions="Toast the bread.",
        source_url="x"
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    db.add(RecipeIngredient(recipe_id=recipe.id, ingredient="bread"))
    db.commit()

    rec_id = recipe.id
    db.close()

    # LIST recipes
    r = client.get("/recipes/")
    assert r.status_code == 200
    assert len(r.json()) == 1

    # GET specific recipe
    r = client.get(f"/recipes/{rec_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Toast"

    # DELETE recipe
    r = client.delete(f"/recipes/{recipe.id}")
    assert r.status_code == 200
    assert r.json()["message"] == "Recipe deleted."

    # LIST again — should now be empty
    r = client.get("/recipes/")
    assert r.status_code == 200
    assert len(r.json()) == 0

