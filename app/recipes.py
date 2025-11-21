# app/recipes.py
"""
===============================================================================
recipes.py — Extracting, Saving, and Managing Recipes
===============================================================================

What this file does (in plain English):

This file provides the API endpoints that deal with recipes:

1. /recipes/extract
   - Takes a video URL (YouTube, TikTok, Instagram, etc.)
   - Uses downloader.py to download the audio
   - Uses gemini.py to extract a recipe (title, ingredients, instructions)
   - Saves recipe + ingredients to the database
   - Returns the stored recipe

2. /recipes/           (GET)
   - Returns all recipes for the logged-in user

3. /recipes/{id}       (GET)
   - Returns a single recipe if the user owns it

4. /recipes/{id}       (DELETE)
   - Deletes recipe + its ingredients

This file does *not* do any heavy AI work. It delegates:
- Audio processing to downloader.py
- Recipe extraction to gemini.py

Its job is simply to coordinate these steps and store the results.
===============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .auth import get_current_user
from .db import get_db
from .models import Recipe, RecipeIngredient
from .services.downloader import download_audio
from .services.gemini import extract_recipe

router = APIRouter()


# ---------------------------------------------------------------------------
# Helper: Convert ORM Recipe → Python dict including ingredients
# ---------------------------------------------------------------------------
def recipe_to_dict(recipe: Recipe):
    return {
        "id": recipe.id,
        "title": recipe.title,
        "instructions": recipe.instructions,
        "source_url": recipe.source_url,
        "ingredients": [ing.ingredient for ing in recipe.ingredients],
        "created_at": str(recipe.created_at),
    }


# ---------------------------------------------------------------------------
# Endpoint: Extract & Save Recipe from Video URL
# ---------------------------------------------------------------------------
@router.post("/extract")
def extract_recipe_from_url(
    url: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Extract a recipe from a video URL and save it to the database.

    Steps:
    ------
    1. Download audio using downloader.py
    2. Run Gemini extraction using gemini.py
    3. Create Recipe entry in the database
    4. Create RecipeIngredient entries
    5. Return the stored recipe with its ingredients
    """

    # 1. Download audio
    audio_path = download_audio(url)

    # 2. Extract recipe via Gemini
    data = extract_recipe(audio_path)

    # 3. Save recipe
    recipe = Recipe(
        user_id=user.id,
        title=data["title"],
        instructions=data["instructions"],
        source_url=url,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    # 4. Save ingredients
    for ing in data["ingredients"]:
        row = RecipeIngredient(recipe_id=recipe.id, ingredient=ing)
        db.add(row)
    db.commit()
    db.refresh(recipe)

    return recipe_to_dict(recipe)


# ---------------------------------------------------------------------------
# Endpoint: Get all recipes for the user
# ---------------------------------------------------------------------------
@router.get("/")
def list_recipes(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipes = (
        db.query(Recipe)
        .filter(Recipe.user_id == user.id)
        .order_by(Recipe.created_at.desc())
        .all()
    )
    return [recipe_to_dict(r) for r in recipes]


# ---------------------------------------------------------------------------
# Endpoint: Get one recipe
# ---------------------------------------------------------------------------
@router.get("/{recipe_id}")
def get_recipe(
    recipe_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == user.id
    ).first()

    if not recipe:
        raise HTTPException(404, "Recipe not found.")

    return recipe_to_dict(recipe)


# ---------------------------------------------------------------------------
# Endpoint: Delete recipe
# ---------------------------------------------------------------------------
@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == user.id
    ).first()

    if not recipe:
        raise HTTPException(404, "Recipe not found.")

    db.delete(recipe)
    db.commit()

    return {"message": "Recipe deleted."}

