# app/pantry.py
"""
Simple pantry endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .db import get_db
from .auth import get_current_user
from .models import PantryItem

router = APIRouter()

@router.post("/add")
def add_item(name: str, 
             user=Depends(get_current_user), 
             db: Session = Depends(get_db)):
    item = PantryItem(user_id=user.id, ingredient=name)
    db.add(item)
    db.commit()
    return {"message": "added", "ingredient": name}

@router.get("/")
def list_items(user=Depends(get_current_user), 
               db: Session = Depends(get_db)):
    items = db.query(PantryItem).filter(PantryItem.user_id == user.id).all()
    return [i.ingredient for i in items]
