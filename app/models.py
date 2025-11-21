# app/models.py
"""
==================================================================
models.py — Database Table Definitions (Using SQLAlchemy ORM)
==================================================================
What this file does (in plain English):

This file defines the **structure of our database tables**.  
Instead of writing raw SQL like:

    CREATE TABLE users (...);

we use a Python library called SQLAlchemy ORM. Each class in this
file represents a table in the database, and each class attribute
represents a column in that table.

Our app needs to store several types of data:

1. Users (email, password, etc.)
2. Recipes (title, instructions, link to video)
3. Ingredients for each recipe
4. Items in a user’s pantry

Each of these corresponds to a class:
- User
- Recipe
- RecipeIngredient
- PantryItem

Each class:
- describes what information we store,
- defines relationships between tables (e.g., each recipe belongs to a user),
- automatically creates unique IDs for each entry.

These models are the backbone of the app — all saving, querying,
and recommendations are built on top of this structure.

Even if you've never used a database before, think of this file
as defining the “data shapes” that our app uses.
==================================================================
"""

import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

# Base class required by SQLAlchemy. All models inherit from this.
Base = declarative_base()


def generate_uuid() -> str:
    """
    Generates a random UUID string to use as a primary key.
    UUIDs are unique across all devices and databases.
    """
    return str(uuid.uuid4())


class User(Base):
    """
    The 'users' table — stores account information for each user.
    """
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships:
    # user.recipes → list of Recipe objects
    recipes = relationship("Recipe", back_populates="user", cascade="all, delete-orphan")

    # user.pantry_items → list of PantryItem objects
    pantry_items = relationship("PantryItem", back_populates="user", cascade="all, delete-orphan")


class Recipe(Base):
    """
    The 'recipes' table — stores each recipe the user has saved or extracted.
    """
    __tablename__ = "recipes"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    instructions = Column(Text, nullable=False)
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="recipes")

    # recipe.ingredients → list of RecipeIngredient objects
    ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )


class RecipeIngredient(Base):
    """
    The 'recipe_ingredients' table — stores ingredients for a recipe.

    - Each row is a single ingredient.
    - A recipe may have many rows in this table.
    """
    __tablename__ = "recipe_ingredients"

    id = Column(String, primary_key=True, default=generate_uuid)
    recipe_id = Column(String, ForeignKey("recipes.id"), nullable=False, index=True)
    ingredient = Column(String, nullable=False, index=True)

    recipe = relationship("Recipe", back_populates="ingredients")


class PantryItem(Base):
    """
    The 'pantry_items' table — stores items that the user currently has
    in their pantry. These will be used to calculate missing ingredients
    in the grocery recommender.
    """
    __tablename__ = "pantry_items"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    ingredient = Column(String, nullable=False, index=True)
    barcode = Column(String, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="pantry_items")
