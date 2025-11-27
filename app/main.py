# app/main.py
"""
==================================================================
main.py — FastAPI Application Startup File
==================================================================
What this file does (in plain English):

This is the main entry point for the entire web app.  
When you run:

    uvicorn app.main:app --reload

FastAPI looks inside this file for the variable named "app".

This file is responsible for:

1. Creating the FastAPI application object.
2. Setting up CORS so our frontend (e.g., React, Svelte, etc.)
   can connect to the backend safely.
3. Initializing our database tables (for local development).
4. Registering our route modules:
       - auth.py      (signup/login)
       - recipes.py   (extract recipe from link, CRUD)
       - grocery.py   (ingredient recommendation engine)
5. Providing a simple /health endpoint so we can test if the app
   is running.

Think of this file as the "control center" of the backend.
It doesn't contain business logic itself — instead, it connects
all the parts of the system together in one place.
==================================================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from . import auth, recipes, pantry, grocery

# Automatically create tables if they don't exist
# Base.metadata.create_all(bind=engine)

# Create the FastAPI application instance.
app = FastAPI(
    title="ReciPal",
    version="0.1.0",
    description="Backend API for recipe extraction and pantry-based grocery recommendations.",
)

# Populate demo data IF database is empty
# with SessionLocal() as db:
#     initialize_demo_data(db)

# Allow frontend apps to talk to the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # ok for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register (include) all route files.
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
app.include_router(pantry.router, prefix="/pantry", tags=["pantry"])
app.include_router(grocery.router, prefix="/grocery", tags=["grocery"])


@app.get("/health")
def health_check():
    """
    Simple endpoint to confirm the server is running.
    """
    return {"status": "ok"}