from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from supabase import create_client
from supabase_auth.errors import AuthApiError
from pydantic import BaseModel
import os

router = APIRouter()

security = HTTPBearer()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"]) 
# Optional service-role client: useful for server-side operations that need to bypass
# row-level security (RLS). Set `SUPABASE_SERVICE_ROLE_KEY` in your server `.env`
# only — never expose the service role key to client-side code.
service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
service_supabase = None
if service_role_key:
    service_supabase = create_client(os.environ["SUPABASE_URL"], service_role_key)

JWT_SECRET = os.environ["SUPABASE_JWT_SECRET"]

class AuthRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    username: str

@router.post("/signup")
def signup(auth: SignupRequest):
    """Sign up a new user with email and password."""
    try:
        # Create auth user in Supabase
        auth_response = supabase.auth.sign_up({"email": auth.email, "password": auth.password})

        # Get the user ID from auth response
        user_id = auth_response.user.id

        # Use service role client if available (bypasses RLS). Otherwise attempt
        # the insert with the anon client (may fail if RLS blocks anonymous writes).
        insert_client = service_supabase if service_supabase is not None else supabase
        insert_client.table("user").insert({
            "uid": user_id,
            "username": auth.username
        }).execute()
        
        return {
            "message": "User signed up successfully. Please check your email to confirm.",
            "user_id": user_id,
            "username": auth.username
        }
    except AuthApiError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user profile: {str(e)}")

@router.post("/login")
def login(auth: AuthRequest):
    """Log in a user and return a JWT token."""
    try:
        auth_response = supabase.auth.sign_in_with_password({"email": auth.email, "password": auth.password})
        if not auth_response.session:
            raise HTTPException(status_code=400, detail="Login failed.")
        return {"access_token": auth_response.session.access_token, "token_type": "bearer"}
    except AuthApiError as e:
        raise HTTPException(status_code=400, detail=str(e))

def verify_token(credentials=Depends(HTTPBearer())):
    token = credentials.credentials
    try:
        # Decode JWT without verification first to check structure
        # Supabase uses the JWT secret for signing 
        decoded = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=["HS256"],
            options={"verify_aud": False}  # Supabase JWTs don't always have standard aud
        )
        return decoded
    except JWTError as e:
        raise HTTPException(401, f"Invalid token: {str(e)}")