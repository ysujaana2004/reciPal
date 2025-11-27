import os
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError("Supabase credentials missing")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


# ==================== Table Name Constants ====================

class Tables:
    """Database table names as constants."""
    USER = "user"
    RECIPES = "recipes"
    PANTRY = "pantry_items"
    INGREDIENTS = "ingredients"
    GROCERY = "grocery_recommendations"


# ==================== Helper Functions ====================

def get_user_id_from_uid(uid: str) -> int:
    """
    Convert Supabase Auth UUID to your custom user table's integer ID.
    
    Args:
        uid: The UUID from Supabase Auth (from JWT token)
        
    Returns:
        int: The integer user ID from your user table
        
    Raises:
        HTTPException: If user not found
    """
    try:
        resp = supabase.table(Tables.USER).select("id").eq("uid", uid).execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="User not found")
        return resp.data[0]["id"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def get_user_by_id(user_id: int) -> dict:
    """
    Get user profile by integer ID.
    
    Args:
        user_id: Integer ID from user table
        
    Returns:
        dict: User data including id, username, uid
    """
    try:
        resp = supabase.table(Tables.USER).select("*").eq("id", user_id).execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="User not found")
        return resp.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def get_user_by_uid(uid: str) -> dict:
    """
    Get user profile by Supabase Auth UUID.
    
    Args:
        uid: UUID from Supabase Auth
        
    Returns:
        dict: User data including id, username, uid
    """
    try:
        resp = supabase.table(Tables.USER).select("*").eq("uid", uid).execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="User not found")
        return resp.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def ensure_user_owns_resource(user_id: int, table: str, resource_id: int, id_column: str = "id"):
    """
    Verify that a user owns a specific resource (recipe, pantry item, etc.)
    
    Args:
        user_id: The user's integer ID
        table: Table name (e.g., "recipes")
        resource_id: The resource's ID
        id_column: Name of the ID column (default: "id")
        
    Raises:
        HTTPException: If resource doesn't exist or user doesn't own it
    """
    try:
        resp = supabase.table(table).select("user_id").eq(id_column, resource_id).execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail=f"{table} not found")
        if resp.data[0]["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def paginate_query(query, page: int = 1, page_size: int = 20):
    """
    Add pagination to a Supabase query.
    
    Args:
        query: Supabase query builder
        page: Page number (1-indexed)
        page_size: Items per page
        
    Returns:
        Modified query with range limits
    """
    start = (page - 1) * page_size
    end = start + page_size - 1
    return query.range(start, end)
