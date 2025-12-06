# tests/test_models.py
"""
Tests for models.py

These tests verify:
- Tables can be created from Base.metadata
- Basic CRUD operations work for User, Recipe, RecipeIngredient, PantryItem
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, User, Recipe, RecipeIngredient, PantryItem

def create_test_session():
    """
    Create an in-memory SQLite database and return a session.
    This keeps tests isolated and fast.
    """
    engine = create_engine("sqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        future=True,
    )
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()

def test_create_user_and_pantry_items():
    db = create_test_session()

    # Create a user
    user = User(email="test@example.com", password_hash="hashed_pw")
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"

    # Add a pantry item
    item = PantryItem(user_id=user.id, ingredient="onion", barcode="0123456789")
    db.add(item)
    db.commit()
    db.refresh(item)

    assert item.id is not None
    assert item.user_id == user.id
    assert item.ingredient == "onion"

    # Relationship: user.pantry_items should contain the item
    assert len(user.pantry_items) == 1
    assert user.pantry_items[0].ingredient == "onion"

def test_create_recipe_and_ingredients():
    db = create_test_session()

    # Create user
    user = User(email="chef@example.com", password_hash="hashed_pw")
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create recipe
    recipe = Recipe(
        user_id=user.id,
        title="Test Pasta",
        instructions="Boil pasta. Add sauce.",
        source_url="https://example.com/video",
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    assert recipe.id is not None
    assert recipe.title == "Test Pasta"
    assert recipe.user_id == user.id

    # Add ingredients
    ing1 = RecipeIngredient(recipe_id=recipe.id, ingredient="pasta")
    ing2 = RecipeIngredient(recipe_id=recipe.id, ingredient="tomato sauce")

    db.add_all([ing1, ing2])
    db.commit()

    # Reload recipe with ingredients
    db.refresh(recipe)
    assert len(recipe.ingredients) == 2
    ingredient_names = {i.ingredient for i in recipe.ingredients}
    assert ingredient_names == {"pasta", "tomato sauce"}
