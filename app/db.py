# app/db.py
"""
==================================================================
db.py — Database Connection and Session Helper
==================================================================
What this file does (in plain English):

This file sets up the connection to our database.

Every time our app needs to store or retrieve information
(recipes, ingredients, user accounts, pantry items, etc.),
it must “talk” to the database. Instead of opening a new
database connection manually each time, we create a system here
that:

1. Creates a single database engine (the object that knows how to
   talk to the database).

2. Creates a SessionLocal object — something our routes use to
   open a short-lived “database session”. A session is like opening
   a temporary lane to the database, using it, and closing it after.

3. Provides a get_db() function that FastAPI uses as a dependency.
   Any route that needs the database simply writes:
       def endpoint(db = Depends(get_db)):
   FastAPI will automatically:
     - open a database session,
     - pass it to the route,
     - close it when the route finishes.

4. Works with any database:
     - Supabase Postgres (in production)
     - local SQLite file (during development and testing)

You don't need to modify anything here unless you're switching to
a totally different database technology.
==================================================================
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# DATABASE_URL tells SQLAlchemy which database to connect to.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# SQLite requires a special flag, other databases will ignore it.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Engine: the core object that talks to the database.
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    future=True,
    echo=False,  # change to True to see raw SQL logs
)

# SessionLocal: produces new database sessions when needed.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)

def get_db():
    """
    get_db() — Dependency used by FastAPI routes

    When a route needs a database session, FastAPI will:
      - call this function,
      - yield a new SessionLocal(),
      - automatically close it afterwards.

    This prevents database connections from being left open.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

