from fastapi import APIRouter, Depends
from .auth import verify_token

router = APIRouter()

@router.get("/me")
def get_me(user=Depends(verify_token)):
    return {"id": user["sub"], "email": user["email"]}