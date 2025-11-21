# app/grocery.py
"""
======================================================================
grocery.py — Ingredient Recommendation Engine
======================================================================

What this file does (in plain English):

This file contains the logic that powers the “grocery recommender”.

The goal:
--------
Given:
    - The ingredients the user *already* has in their pantry, and
    - The recipes the user has saved to their account

We recommend **new ingredients** that would allow the user to make
the most additional recipes.

Example:
--------
If a user has 20 saved recipes but their pantry ingredients allow
them to cook only 8 of them, this system figures out:

    “Which ONE ingredient, if purchased,
     unlocks the greatest number of NEW recipes?”

Then the next-best ingredient, and so on.

How it works:
-------------
1. Load all pantry items for the user.
2. Load all ingredients for all the user’s recipes.
3. For each recipe:
       missing_ingredients = recipe.ingredients - pantry.ingredients
4. Count how many recipes each missing ingredient would unlock.
5. Sort from most useful → least.
6. Return a clean JSON list.

This should be very fast even with many recipes because all operations
are simple set-based comparisons in Python.

This file does *not* modify the database—it only reads information
and computes a recommendation.
======================================================================
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .auth import get_current_user
from .db import get_db
from .models import PantryItem, Recipe, RecipeIngredient

router = APIRouter()


# -------------------------------------------------------------------
# Helper Function:
#   Convert a list of ORM objects into a lowercase string set
# -------------------------------------------------------------------
def normalize_ingredients(items):
    """
    Given a list of ingredient strings or PantryItem/RecipeIngredient objects,
    convert them into a clean lowercase set.

    This makes comparison easy and removes inconsistencies like:
        "Onion", "onion ", " onion", "ONION"
    """
    result = set()
    for item in items:
        # If item is ORM object → extract ingredient field
        if hasattr(item, "ingredient"):
            name = item.ingredient
        else:
            name = item

        if name is None:
            continue

        cleaned = name.strip().lower()
        result.add(cleaned)

    return result


# -------------------------------------------------------------------
# Endpoint: Recommend Grocery Items
# -------------------------------------------------------------------
@router.get("/recommendations")
def recommend_ingredients(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Main endpoint for the grocery recommender.

    Steps:
    ------
    1. Load the user's pantry items.
    2. Load all recipes belonging to the user.
    3. Load all ingredients for each recipe.
    4. Compute which ingredients are missing.
    5. Count how many recipes each new ingredient would unlock.
    6. Return a sorted list from most → least useful.
    """

    # ---------------------------------------------------------------
    # STEP 1: Load user's pantry ingredients
    # ---------------------------------------------------------------
    pantry_rows = (
        db.query(PantryItem)
        .filter(PantryItem.user_id == user.id)
        .all()
    )
    pantry_set = normalize_ingredients(pantry_rows)

    # ---------------------------------------------------------------
    # STEP 2: Load user's recipes (IDs only)
    # ---------------------------------------------------------------
    recipe_rows = (
        db.query(Recipe)
        .filter(Recipe.user_id == user.id)
        .all()
    )

    if not recipe_rows:
        return []  # no recipes → no recommendations

    recipe_ids = [r.id for r in recipe_rows]

    # ---------------------------------------------------------------
    # STEP 3: Load all ingredients for these recipes
    # ---------------------------------------------------------------
    ingredient_rows = (
        db.query(RecipeIngredient)
        .filter(RecipeIngredient.recipe_id.in_(recipe_ids))
        .all()
    )

    # Build a mapping: recipe_id → set of ingredients
    recipe_map = {}
    for row in ingredient_rows:
        recipe_map.setdefault(row.recipe_id, set()).add(row.ingredient.strip().lower())

    # ---------------------------------------------------------------
    # STEP 4: Compute unlock counts
    # ---------------------------------------------------------------
    unlock_counts = {}

    for recipe_id, ingredient_set in recipe_map.items():
        missing = ingredient_set - pantry_set  # the ingredients user lacks

        for ingredient in missing:
            unlock_counts[ingredient] = unlock_counts.get(ingredient, 0) + 1

    # ---------------------------------------------------------------
    # STEP 5: Sort recommendations
    # ---------------------------------------------------------------
    recommendations = sorted(
        [
            {"ingredient": ing, "unlocks": count}
            for ing, count in unlock_counts.items()
        ],
        key=lambda x: x["unlocks"],
        reverse=True,
    )

    return recommendations
