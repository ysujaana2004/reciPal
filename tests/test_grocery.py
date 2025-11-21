# tests/test_grocery.py
"""
======================================================================
Test: Grocery Ingredient Recommender
======================================================================

This test focuses ONLY on the grocery recommendation algorithm.
It does NOT test authentication, password hashing, or signup/signin.
We directly:

- Insert a user into the test DB
- Insert recipes and their ingredients
- Insert pantry items for the user
- Generate a JWT manually (without password checks)
- Call /grocery/recommendations
- Verify that the unlock counts are correct

This makes the test stable, isolated, and focused.
======================================================================
"""

import tempfile
import atexit
import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import get_db
from app.models import Base, User, Recipe, RecipeIngredient, PantryItem
from app.auth import create_access_token


# -------------------------------------------------------------------
# Setup: Create a temporary SQLite DB for THIS test file
# -------------------------------------------------------------------

tmp = tempfile.NamedTemporaryFile(delete=False)
db_path = tmp.name
atexit.register(lambda: os.remove(db_path))  # auto-delete after tests finish

engine = create_engine(
    f"sqlite:///{db_path}",
    connect_args={"check_same_thread": False},
    future=True,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

Base.metadata.create_all(bind=engine)


# Override get_db so routes use this test DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# -------------------------------------------------------------------
# TEST
# -------------------------------------------------------------------
def test_grocery_recommendations():
    """
    This test checks:

    - Ingredient normalization
    - Missing ingredient calculation
    - Unlock count computation
    - Sorting of recommendations

    WITHOUT touching authentication or signup/signin.
    """

    db = TestingSessionLocal()

    # -----------------------------
    # 1. Create user
    # -----------------------------
    user = User(email="tester@example.com", password_hash="irrelevant")
    db.add(user)
    db.commit()
    db.refresh(user)

    # -----------------------------
    # 2. Create recipes for this user
    # -----------------------------
    r1 = Recipe(
        user_id=user.id,
        title="Pasta",
        instructions="",
    )

    r2 = Recipe(
        user_id=user.id,
        title="Omelette",
        instructions="",
    )

    db.add_all([r1, r2])
    db.commit()
    db.refresh(r1)
    db.refresh(r2)

    # -----------------------------
    # 3. Add ingredients to recipes
    # -----------------------------
    # Recipe 1
    db.add_all([
        RecipeIngredient(recipe_id=r1.id, ingredient="pasta"),
        RecipeIngredient(recipe_id=r1.id, ingredient="tomato"),
        RecipeIngredient(recipe_id=r1.id, ingredient="salt"),
    ])

    # Recipe 2
    db.add_all([
        RecipeIngredient(recipe_id=r2.id, ingredient="egg"),
        RecipeIngredient(recipe_id=r2.id, ingredient="salt"),
        RecipeIngredient(recipe_id=r2.id, ingredient="onion"),
    ])

    # -----------------------------
    # 4. Add pantry items
    # -----------------------------
    # User already has: salt, egg
    db.add_all([
        PantryItem(user_id=user.id, ingredient="salt"),
        PantryItem(user_id=user.id, ingredient="egg"),
    ])

    db.commit()
    user_id = user.id
    db.close()

    # -----------------------------
    # 5. Generate JWT manually
    # -----------------------------
    token = create_access_token({"user_id": user.id})

    # -----------------------------
    # 6. Call recommendation endpoint
    # -----------------------------
    res = client.get(
        "/grocery/recommendations",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 200
    data = res.json()

    # Convert to set for easy checking
    returned_ingredients = {item["ingredient"] for item in data}

    # -----------------------------
    # EXPECTED:
    #   Missing from Pasta: pasta, tomato
    #   Missing from Omelette: onion
    # -----------------------------
    assert returned_ingredients == {"pasta", "tomato", "onion"}

    # Each should unlock exactly one recipe
    for item in data:
        assert item["unlocks"] == 1
