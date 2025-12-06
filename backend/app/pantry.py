# app/pantry.py
"""
===============================================================================
pantry.py — Pantry Management Endpoints
===============================================================================

What this file does (in plain English):

This file provides API endpoints for managing a user's pantry inventory:

1. POST /pantry/           - Add or update an item in pantry (upsert)
2. GET  /pantry/           - List all items in user's pantry
3. PUT  /pantry/{item_id}  - Update quantity of a specific item
4. DELETE /pantry/{item_id} - Remove item from pantry
5. POST /pantry/check      - Check which recipe ingredients user has/needs

All operations are user-specific and require authentication.
===============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from .db import supabase, get_user_id_from_uid, ensure_user_owns_resource, Tables
from .auth import verify_token

router = APIRouter()


class PantryItemCreate(BaseModel):
    ingredient_name: str
    quantity: float
    unit: str = "pieces"


class PantryItemUpdate(BaseModel):
    quantity: float
    unit: Optional[str] = None


class RecipeCheck(BaseModel):
    ingredients: List[str]


@router.post("/")
def add_or_update_item(item: PantryItemCreate, token_data: dict = Depends(verify_token)):
    """Add a new item to pantry or update quantity if it already exists (upsert)."""
    
    if supabase is None:
        raise HTTPException(500, "Supabase client is not configured.")
    
    user_id = get_user_id_from_uid(token_data.get("sub"))
    
    payload = {
        "user_id": user_id,
        "ingredient_name": item.ingredient_name.lower().strip(),
        "quantity": item.quantity,
        "unit": item.unit
    }
    
    # Check if item already exists
    existing = supabase.table(Tables.PANTRY).select("*").eq(
        "user_id", user_id
    ).eq(
        "ingredient_name", item.ingredient_name.lower().strip()
    ).execute()
    
    if existing.data:
        # Update existing item
        item_id = existing.data[0]["id"]
        resp = supabase.table(Tables.PANTRY).update({
            "quantity": item.quantity,
            "unit": item.unit,
            "updated_at": "now()"
        }).eq("id", item_id).execute()
    else:
        # Insert new item
        resp = supabase.table(Tables.PANTRY).insert(payload).execute()
    
    if not resp.data:
        raise HTTPException(500, "Failed to add item to pantry.")
    
    return resp.data[0]


@router.get("/")
def list_pantry_items(token_data: dict = Depends(verify_token)):
    """Get all items in the user's pantry."""
    
    if supabase is None:
        raise HTTPException(500, "Supabase client is not configured.")
    
    user_id = get_user_id_from_uid(token_data.get("sub"))
    
    resp = supabase.table(Tables.PANTRY)\
        .select("*")\
        .eq("user_id", user_id)\
        .order("ingredient_name")\
        .execute()
    
    return resp.data or []


@router.get("/{item_id}")
def get_pantry_item(item_id: int, token_data: dict = Depends(verify_token)):
    """Get a specific pantry item by ID."""
    
    if supabase is None:
        raise HTTPException(500, "Supabase client is not configured.")
    
    user_id = get_user_id_from_uid(token_data.get("sub"))
    
    resp = supabase.table(Tables.PANTRY)\
        .select("*")\
        .eq("id", item_id)\
        .eq("user_id", user_id)\
        .execute()
    
    if not resp.data:
        raise HTTPException(404, "Pantry item not found.")
    
    return resp.data[0]


@router.put("/{item_id}")
def update_pantry_item(item_id: int, update: PantryItemUpdate, token_data: dict = Depends(verify_token)):
    """Update the quantity (and optionally unit) of a pantry item."""
    
    if supabase is None:
        raise HTTPException(500, "Supabase client is not configured.")
    
    user_id = get_user_id_from_uid(token_data.get("sub"))
    
    # Verify ownership
    ensure_user_owns_resource(user_id, Tables.PANTRY, item_id)
    
    # Build update payload
    payload = {"quantity": update.quantity}
    if update.unit is not None:
        payload["unit"] = update.unit
    
    resp = supabase.table(Tables.PANTRY)\
        .update(payload)\
        .eq("id", item_id)\
        .execute()
    
    if not resp.data:
        raise HTTPException(500, "Failed to update pantry item.")
    
    return resp.data[0]


@router.delete("/{item_id}")
def delete_pantry_item(item_id: int, token_data: dict = Depends(verify_token)):
    """Remove an item from the pantry."""
    
    if supabase is None:
        raise HTTPException(500, "Supabase client is not configured.")
    
    user_id = get_user_id_from_uid(token_data.get("sub"))
    
    # Verify ownership
    ensure_user_owns_resource(user_id, Tables.PANTRY, item_id)
    
    resp = supabase.table(Tables.PANTRY)\
        .delete()\
        .eq("id", item_id)\
        .execute()
    
    if not resp.data:
        raise HTTPException(404, "Pantry item not found.")
    
    return {"message": "Pantry item deleted successfully."}


@router.get("/check/recipe/{recipe_id}")
def check_recipe_by_id(recipe_id: int, token_data: dict = Depends(verify_token)):
    """
    Check if user has ingredients for a specific recipe from their saved recipes.
    
    This is the PREFERRED method - automatically fetches recipe ingredients from
    the database and checks against user's pantry. Returns detailed information
    about what the user has and what they need.
    
    Args:
        recipe_id: The ID of the recipe to check
        
    Returns:
        - recipe_id: ID of the recipe
        - recipe_title: Title of the recipe
        - available: List of ingredients user has (with quantities)
        - missing: List of ingredients user needs to buy
        - can_make: Boolean indicating if user can make the recipe
    """
    
    if supabase is None:
        raise HTTPException(500, "Supabase client is not configured.")
    
    user_id = get_user_id_from_uid(token_data.get("sub"))
    
    # 1. Fetch the recipe from database
    recipe_resp = supabase.table(Tables.RECIPES)\
        .select("id, title, ingredients")\
        .eq("id", recipe_id)\
        .execute()
    
    if not recipe_resp.data:
        raise HTTPException(404, "Recipe not found.")
    
    recipe = recipe_resp.data[0]
    
    # 2. Parse ingredients (assuming it's stored as JSON array)
    if isinstance(recipe["ingredients"], str):
        # If stored as comma-separated string: "tomatoes, pasta, basil"
        recipe_ingredients = [ing.strip().lower() for ing in recipe["ingredients"].split(",")]
    elif isinstance(recipe["ingredients"], list):
        # If stored as JSON array: ["tomatoes", "pasta", "basil"]
        recipe_ingredients = [ing.lower().strip() for ing in recipe["ingredients"]]
    else:
        raise HTTPException(400, "Invalid ingredients format in recipe.")
    
    # 3. Check user's pantry for matching ingredients
    pantry_resp = supabase.table(Tables.PANTRY)\
        .select("ingredient_name, quantity, unit")\
        .eq("user_id", user_id)\
        .in_("ingredient_name", recipe_ingredients)\
        .execute()
    
    available = [item["ingredient_name"] for item in pantry_resp.data]
    missing = [ing for ing in recipe_ingredients if ing not in available]
    
    return {
        "recipe_id": recipe["id"],
        "recipe_title": recipe["title"],
        "available": pantry_resp.data,
        "missing": missing,
        "total_ingredients": len(recipe_ingredients),
        "have_count": len(available),
        "need_count": len(missing),
        "can_make": len(missing) == 0
    }


@router.post("/check")
def check_recipe_ingredients(check: RecipeCheck, token_data: dict = Depends(verify_token)):
    """
    Check which ingredients from a manual list the user has in their pantry.
    
    NOTE: Prefer using GET /pantry/check/recipe/{recipe_id} for saved recipes.
    This endpoint is useful for checking external recipes or custom ingredient lists.
    
    Returns:
        - available: List of ingredients user has
        - missing: List of ingredients user needs
    """
    
    if supabase is None:
        raise HTTPException(500, "Supabase client is not configured.")
    
    user_id = get_user_id_from_uid(token_data.get("sub"))
    
    # Normalize ingredient names
    recipe_ingredients = [ing.lower().strip() for ing in check.ingredients]
    
    # Get user's pantry items that match recipe ingredients
    resp = supabase.table(Tables.PANTRY)\
        .select("ingredient_name, quantity, unit")\
        .eq("user_id", user_id)\
        .in_("ingredient_name", recipe_ingredients)\
        .execute()
    
    available = [item["ingredient_name"] for item in resp.data]
    missing = [ing for ing in recipe_ingredients if ing not in available]
    
    return {
        "available": resp.data,
        "missing": missing,
        "total_ingredients": len(recipe_ingredients),
        "have_count": len(available),
        "need_count": len(missing)
    }
