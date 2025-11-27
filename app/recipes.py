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

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from .db import supabase
from .services.downloader import download_audio
from .services.gemini import extract_recipe
from .auth import verify_token

router = APIRouter()


class RecipeCreate(BaseModel):
   title: str
   instructions: str
   ingredients: list[str]
   source_url: str = ""



@router.post("/extract")
def extract_recipe_from_url(url: str, token_data: dict = Depends(verify_token)):
   """Extract a recipe from a video URL and save it to Supabase.
   
   Requires authentication. The user ID is extracted from the JWT token.
   """

   if supabase is None:
      raise HTTPException(500, "Supabase client is not configured.")

   # Get the UUID from the JWT token
   user_uid = token_data.get("sub")
   if not user_uid:
      raise HTTPException(401, "Invalid token: missing user ID")

   # Look up the integer user_id from the user table
   user_resp = supabase.table("user").select("id").eq("uid", user_uid).execute()
   if not user_resp.data:
      raise HTTPException(404, "User profile not found. Please contact support.")
   
   user_id = user_resp.data[0]["id"]

   audio_path = download_audio(url)
   data = extract_recipe(audio_path)

   payload = {
      "user_id": user_id,
      "title": data["title"],
      "instructions": data["instructions"],
      "ingredients": data["ingredients"],  # stored as JSONB
      "source_url": url,
   }

   resp = supabase.table("recipes").insert(payload).execute()
   if not resp.data:
      raise HTTPException(500, "Failed to save recipe to Supabase.")

   recipe = resp.data[0]
   return recipe


@router.post("/")
def create_recipe(recipe: RecipeCreate, token_data: dict = Depends(verify_token)):
   """Manually create a recipe.
   
   Requires authentication. Adds a recipe directly without URL extraction.
   """

   if supabase is None:
      raise HTTPException(500, "Supabase client is not configured.")

   # Get the UUID from the JWT token
   user_uid = token_data.get("sub")
   if not user_uid:
      raise HTTPException(401, "Invalid token: missing user ID")

   # Look up the integer user_id from the user table
   user_resp = supabase.table("user").select("id").eq("uid", user_uid).execute()
   if not user_resp.data:
      raise HTTPException(404, "User profile not found. Please contact support.")
   
   user_id = user_resp.data[0]["id"]

   payload = {
      "user_id": user_id,
      "title": recipe.title,
      "instructions": recipe.instructions,
      "ingredients": recipe.ingredients,
      "source_url": recipe.source_url,
   }

   resp = supabase.table("recipes").insert(payload).execute()
   if not resp.data:
      raise HTTPException(500, "Failed to save recipe to Supabase.")

   return resp.data[0]


@router.get("/")
def list_recipes(token_data: dict = Depends(verify_token)):
   """Return all recipes for the logged-in user.
   
   Requires authentication. Only returns recipes owned by the authenticated user.
   """

   if supabase is None:
      raise HTTPException(500, "Supabase client is not configured.")

   # Get the UUID from the JWT token
   user_uid = token_data.get("sub")
   if not user_uid:
      raise HTTPException(401, "Invalid token: missing user ID")

   # Look up the integer user_id from the user table
   user_resp = supabase.table("user").select("id").eq("uid", user_uid).execute()
   if not user_resp.data:
      raise HTTPException(404, "User profile not found. Please contact support.")
   
   user_id = user_resp.data[0]["id"]

   query = supabase.table("recipes").select("*").eq("user_id", user_id)
   resp = query.order("created_at", desc=True).execute()
   return resp.data or []


@router.get("/{recipe_id}")
def get_recipe(recipe_id: int, token_data: dict = Depends(verify_token)):
   """Return a single recipe by id.
   
   Requires authentication. Only returns the recipe if it belongs to the authenticated user.
   """

   if supabase is None:
      raise HTTPException(500, "Supabase client is not configured.")

   # Get the UUID from the JWT token
   user_uid = token_data.get("sub")
   if not user_uid:
      raise HTTPException(401, "Invalid token: missing user ID")

   # Look up the integer user_id from the user table
   user_resp = supabase.table("user").select("id").eq("uid", user_uid).execute()
   if not user_resp.data:
      raise HTTPException(404, "User profile not found. Please contact support.")
   
   user_id = user_resp.data[0]["id"]

   query = supabase.table("recipes").select("*").eq("id", recipe_id).eq("user_id", user_id)
   resp = query.single().execute()
   if not resp.data:
      raise HTTPException(404, "Recipe not found or you don't have permission to view it.")

   return resp.data


@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, token_data: dict = Depends(verify_token)):
   """Delete a recipe by id.
   
   Requires authentication. Only deletes the recipe if it belongs to the authenticated user.
   """

   if supabase is None:
      raise HTTPException(500, "Supabase client is not configured.")

   # Get the UUID from the JWT token
   user_uid = token_data.get("sub")
   if not user_uid:
      raise HTTPException(401, "Invalid token: missing user ID")

   # Look up the integer user_id from the user table
   user_resp = supabase.table("user").select("id").eq("uid", user_uid).execute()
   if not user_resp.data:
      raise HTTPException(404, "User profile not found. Please contact support.")
   
   user_id = user_resp.data[0]["id"]

   query = supabase.table("recipes").delete().eq("id", recipe_id).eq("user_id", user_id)
   resp = query.execute()
   if not resp.data:
      raise HTTPException(404, "Recipe not found or you don't have permission to delete it.")

   return {"message": "Recipe deleted."}

