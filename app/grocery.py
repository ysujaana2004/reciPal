# app/grocery.py
"""
======================================================================
grocery.py — Ingredient Recommendation Engine
======================================================================

What this file does (in plain English):

This file contains the logic that powers the "grocery recommender".

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

    "Which ONE ingredient, if purchased,
     unlocks the greatest number of NEW recipes?"

Then the next-best ingredient, and so on.

How it works:
-------------
1. Load all pantry items for the user.
2. Load all ingredients for all the user's recipes.
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

from fastapi import APIRouter, Depends, HTTPException

from .auth import verify_token
from .db import supabase, get_user_id_from_uid, Tables

router = APIRouter()


# -------------------------------------------------------------------
# Helper Function:
#   Convert a list of items into a lowercase string set
# -------------------------------------------------------------------
def normalize_ingredients(items):
    """
    Given a list of ingredient strings or dictionaries with 'ingredient_name',
    convert them into a clean lowercase set.

    This makes comparison easy and removes inconsistencies like:
        "Onion", "onion ", " onion", "ONION"
    """
    result = set()
    for item in items:
        # If item is a dict (from Supabase) → extract ingredient_name field
        if isinstance(item, dict):
            name = item.get("ingredient_name")
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
def recommend_ingredients(token_data: dict = Depends(verify_token)):
    """
    Main endpoint for the grocery recommender.

    Steps:
    ------
    1. Load the user's pantry items.
    2. Load all recipes belonging to the user.
    3. For each recipe, extract ingredients array.
    4. Compute which ingredients are missing.
    5. Count how many recipes each new ingredient would unlock.
    6. Return a sorted list from most → least useful.
    """

    if supabase is None:
        raise HTTPException(500, "Supabase client is not configured.")

    user_id = get_user_id_from_uid(token_data.get("sub"))

    # ---------------------------------------------------------------
    # STEP 1: Load user's pantry ingredients
    # ---------------------------------------------------------------
    pantry_resp = supabase.table(Tables.PANTRY).select("ingredient_name").eq("user_id", user_id).execute()
    pantry_set = normalize_ingredients(pantry_resp.data or [])

    # ---------------------------------------------------------------
    # STEP 2: Load user's recipes with ingredients
    # ---------------------------------------------------------------
    recipes_resp = supabase.table(Tables.RECIPES).select("id, ingredients").eq("user_id", user_id).execute()
    recipes = recipes_resp.data or []

    if not recipes:
        return []  # no recipes → no recommendations

    # ---------------------------------------------------------------
    # STEP 3: Compute unlock counts
    # ---------------------------------------------------------------
    unlock_counts = {}

    for recipe in recipes:
        # Get ingredients array from recipe
        ingredients = recipe.get("ingredients") or []
        
        # Normalize and find missing ingredients
        recipe_set = set(ing.strip().lower() for ing in ingredients if ing)
        missing = recipe_set - pantry_set  # the ingredients user lacks

        for ingredient in missing:
            unlock_counts[ingredient] = unlock_counts.get(ingredient, 0) + 1

    # ---------------------------------------------------------------
    # STEP 4: Sort recommendations
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
