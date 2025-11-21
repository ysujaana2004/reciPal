# app/auth.py
"""
===============================================================================
auth.py — Extremely Simple Authentication (Demo Only)
===============================================================================

This file provides the simplest possible authentication system suitable
for a school project or prototype.

It supports:
    - POST /auth/signup   (create user)
    - POST /auth/signin   (return a simple token)
    - get_current_user    (extracts user from token)

IMPORTANT:
----------
This is NOT secure.
Passwords are stored in plain text.
Tokens are NOT signed.
This is for DEMO PURPOSES ONLY.

But it will:
    - Never randomly break
    - Make it easy to test the whole app
    - Work perfectly with your existing routes
===============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Form
from sqlalchemy.orm import Session

from .db import get_db
from .models import User

DEMO_EMAIL = "demo@recipal.local"
DEMO_PASSWORD = "demo"

router = APIRouter()


def ensure_demo_user(db: Session) -> User:
    """
    Create (if needed) and return a demo user so the app always has
    someone to act as for unauthenticated requests.
    """
    user = db.query(User).filter(User.email == DEMO_EMAIL).first()
    if user:
        return user

    user = User(email=DEMO_EMAIL, password_hash=DEMO_PASSWORD)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ------------------------------------------------------------------------------
# SIGNUP — store user with plain-text password
# ------------------------------------------------------------------------------
@router.post("/signup")
def signup(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if user exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(400, "Email already registered.")

    user = User(email=email, password_hash=password)  # plain text
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "user created", "user_id": user.id}


# ------------------------------------------------------------------------------
# SIGNIN — return a SUPER SIMPLE token: "user-<id>"
# ------------------------------------------------------------------------------
@router.post("/signin")
def signin(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    # Plain-text password check
    if not user or user.password_hash != password:
        raise HTTPException(400, "Invalid credentials.")

    # The token is literally: user-<id>
    token = f"user-{user.id}"
    return {"access_token": token, "token_type": "bearer"}


# ------------------------------------------------------------------------------
# get_current_user — decode token "user-<id>"
# ------------------------------------------------------------------------------
def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Expected header:
        Authorization: Bearer user-<id>

    We simply extract the user ID and return the user object.
    """
    if not authorization:
        # Fall back to the demo user so the UI works without manual login
        return ensure_demo_user(db)

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError
    except ValueError:
        raise HTTPException(401, "Invalid Authorization header format.")

    if not token.startswith("user-"):
        raise HTTPException(401, "Invalid token format.")

    # Extract ID from token
    user_id = token.split("user-")[-1]

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "User not found.")

    return user
