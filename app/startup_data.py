"""
startup_data.py

This file preloads a demo user, demo recipes, and demo pantry items
whenever the backend starts up — ONLY if the database is empty.

This allows us to use the grocery recommender in the demo without
needing to download videos or run Gemini first.
"""

from sqlalchemy.orm import Session
from .models import User, Recipe, RecipeIngredient, PantryItem

DEMO_EMAIL = "demo@recipal.local"
DEMO_PASSWORD = "demo"


def initialize_demo_data(db: Session):
    """
    Only preload data if the database is empty.
    Avoids duplicating rows on each restart.
    """

    # Check if demo user already exists
    existing = db.query(User).filter(User.email == DEMO_EMAIL).first()
    if existing:
        return  # Data already initialized

    # ---------------------------------------------------------------
    # 1. Create DEMO USER
    # ---------------------------------------------------------------
    demo_user = User(email=DEMO_EMAIL, password_hash=DEMO_PASSWORD)
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)

    uid = demo_user.id

    # ---------------------------------------------------------------
    # 2. Preloaded recipes
    # ---------------------------------------------------------------
    recipes = [
        {
            "title": "Simple Omelette",
            "instructions": "Beat eggs, season, cook in pan.",
            "ingredients": ["eggs", "salt", "pepper", "butter"]
        },
        {
            "title": "Pasta Marinara",
            "instructions": "Boil pasta, add sauce, mix.",
            "ingredients": ["pasta", "tomato sauce", "salt", "olive oil"]
        },
        {
            "title": "Grilled Cheese Sandwich",
            "instructions": "Butter bread, add cheese, grill.",
            "ingredients": ["bread", "cheddar cheese", "butter"]
        },
        {
            "title": "Stir Fry Vegetables",
            "instructions": "Cook vegetables with soy sauce.",
            "ingredients": ["onions", "bell peppers", "soy sauce", "oil"]
        }
    ]

    for r in recipes:
        recipe = Recipe(
            user_id=uid,
            title=r["title"],
            instructions=r["instructions"],
            source_url="preloaded",
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)

        # Add ingredients
        for ing in r["ingredients"]:
            db.add(RecipeIngredient(recipe_id=recipe.id, ingredient=ing))

        db.commit()

    # ---------------------------------------------------------------
    # 3. Preloaded pantry
    # ---------------------------------------------------------------
    pantry_items = ["eggs", "salt", "bread"]

    for p in pantry_items:
        db.add(PantryItem(user_id=uid, ingredient=p))

    db.commit()
