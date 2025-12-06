"""
================================================================================
END-TO-END SYSTEM TEST SCRIPT
================================================================================

This script tests your ENTIRE backend system with REAL logic:

- Real login against Supabase Auth
- Real JWT authentication to protected routes
- Real DB writes/reads (Supabase)
- Real grocery recommender logic

USAGE:
------
Start your server:

    uvicorn app.main:app --reload

Then run this script:

    python end_to_end_test.py

REQUIREMENTS:
-------------
- `requests` installed
- Server running locally on http://127.0.0.1:8000
- GOOGLE_API_KEY set
- yt-dlp installed if you enable the Gemini extraction test
- Set env var E2E_GEMINI_TEST_URL=<your_video_url> to run the Gemini test
================================================================================
"""

import requests
import base64
import json
import os
import shutil
import time
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

from app.services.downloader import download_audio
from app.services.gemini import extract_recipe

load_dotenv()

# Load environment variables (looks for .env next to this script)
# load_dotenv(Path(__file__).resolve().parent / ".env")

BASE = "http://127.0.0.1:8000"

# Existing test account (must exist/confirmed in Supabase)
TEST_EMAIL = "shadwking58@gmail.com"
TEST_PASSWORD = "password"

# Optional: provide a YouTube URL (or set E2E_GEMINI_TEST_URL) to
# trigger an audio download + Gemini extraction test in this script.
TEST_GEMINI_VIDEO_URL = False #"https://www.youtube.com/watch?v=9Mpk5pdYAf0"

# Use a small static recipe so we don't require Gemini/download
TEST_RECIPE = {
    "title": "Test Toast with Butter",
    "instructions": "Toast bread. Spread butter. Serve warm.",
    "ingredients": ["bread", "butter"],
    "source_url": "e2e-script",
}


# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def decode_uid(token: str):
    """Decode JWT payload without verification to extract `sub` (Supabase auth UID)."""
    try:
        payload = token.split(".")[1]
        padding = "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        data = json.loads(decoded)
        return data.get("sub")
    except Exception as e:
        print(f"⚠️ Could not decode token: {e}")
        return None


def ensure_user_profile_exists(token: str, email: str):
    """
    Ensure the Supabase `user` table has a row for this auth UID.
    Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in env.
    """
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not service_key:
        raise SystemExit(
            "❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY. "
            "Set these env vars so the test can upsert the user row (RLS-safe)."
        )

    uid = decode_uid(token)
    if not uid:
        raise SystemExit("❌ Could not decode UID from JWT; cannot ensure user profile.")

    client = create_client(url, service_key)
    table = client.table("user")

    try:
        resp = table.select("id").eq("uid", uid).execute()
        if resp.data:
            print("ℹ️ User profile already exists in Supabase.")
            return
    except Exception as exc:
        raise SystemExit(f"❌ Failed to query Supabase user table: {exc}")

    username = email.split("@")[0]
    try:
        insert_resp = table.upsert({"uid": uid, "username": username}).execute()
        if insert_resp.data:
            print("🟢 Created user profile row in Supabase.")
            return
    except Exception as exc:
        raise SystemExit(f"❌ Failed to insert user profile row; check RLS/service key: {exc}")

    raise SystemExit("❌ User profile insert returned no data; check RLS/service key.")


# ------------------------------------------------------------------------------
# STEP 1: SIGN IN → get JWT token
# ------------------------------------------------------------------------------
def do_login(email, password):
    print("\n🔵 SIGNING IN...")
    resp = requests.post(
        f"{BASE}/auth/login",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"},
    )
    print("Response:", resp.text)
    resp.raise_for_status()
    token = resp.json().get("access_token")
    if not token:
        raise RuntimeError("No access_token returned from /auth/login")
    return token


# ------------------------------------------------------------------------------
# STEP 2: CREATE A SIMPLE RECIPE (DB write)
# ------------------------------------------------------------------------------
def create_recipe(token, recipe_payload):
    print("\n🔵 CREATING TEST RECIPE...")
    resp = requests.post(
        f"{BASE}/recipes/",
        json=recipe_payload,
        headers={
            **auth_headers(token),
            "Content-Type": "application/json",
        },
    )
    print("Response:", resp.text)
    resp.raise_for_status()
    return resp.json()


# ------------------------------------------------------------------------------
# STEP 3: LIST RECIPES (DB read)
# ------------------------------------------------------------------------------
def list_recipes(token):
    print("\n🔵 LISTING RECIPES...")
    resp = requests.get(
        f"{BASE}/recipes/",
        headers=auth_headers(token),
    )
    print("Response:", resp.text)
    resp.raise_for_status()
    return resp.json()


# ------------------------------------------------------------------------------
# STEP 4: ADD PANTRY ITEMS (DB upsert)
# ------------------------------------------------------------------------------
def add_pantry_item(token, name, qty=1, unit="pieces"):
    print(f"\n🔵 ADDING PANTRY ITEM: {name}")
    resp = requests.post(
        f"{BASE}/pantry/",
        json={"ingredient_name": name, "quantity": qty, "unit": unit},
        headers={
            **auth_headers(token),
            "Content-Type": "application/json",
        },
    )
    print("Response:", resp.text)
    resp.raise_for_status()
    return resp.json()


# ------------------------------------------------------------------------------
# STEP 5: CHECK RECIPE VS PANTRY (DB read)
# ------------------------------------------------------------------------------
def check_recipe(token, recipe_id):
    print("\n🔵 CHECKING PANTRY VS RECIPE...")
    resp = requests.get(
        f"{BASE}/pantry/check/recipe/{recipe_id}",
        headers=auth_headers(token),
    )
    print("Response:", resp.text)
    resp.raise_for_status()
    return resp.json()


# ------------------------------------------------------------------------------
# STEP 6: GET GROCERY RECOMMENDATIONS (DB read)
# ------------------------------------------------------------------------------
def get_recommendations(token):
    print("\n🔵 GETTING GROCERY RECOMMENDATIONS...")
    resp = requests.get(
        f"{BASE}/grocery/recommendations",
        headers=auth_headers(token),
    )
    print("Response:", resp.text)
    resp.raise_for_status()
    return resp.json()


# ------------------------------------------------------------------------------
# OPTIONAL STEP: DOWNLOAD AUDIO + RUN GEMINI EXTRACTION
# ------------------------------------------------------------------------------
def run_gemini_extraction_test(video_url: str):
    print("\n🔵 DOWNLOADING AUDIO + EXTRACTING RECIPE VIA GEMINI...")
    audio_path = None
    try:
        audio_path = download_audio(video_url)
        print(f"Audio saved to: {audio_path}")

        recipe_data = extract_recipe(audio_path)
        if not recipe_data.get("title"):
            raise RuntimeError("Gemini response missing title.")
        if not recipe_data.get("ingredients"):
            raise RuntimeError("Gemini response missing ingredients list.")
        if not recipe_data.get("instructions"):
            raise RuntimeError("Gemini response missing instructions.")

        print("Gemini recipe extraction succeeded:")
        print(json.dumps(recipe_data, indent=2))
        return recipe_data
    finally:
        if audio_path:
            # Clean up the temporary download directory
            shutil.rmtree(Path(audio_path).parent, ignore_errors=True)


# ------------------------------------------------------------------------------
# MAIN RUNNER
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n==============================================================")
    print("🚀 STARTING END-TO-END SYSTEM TEST")
    print("==============================================================")

    # OPTIONAL: Run Gemini extraction test if URL provided
    if TEST_GEMINI_VIDEO_URL:
        run_gemini_extraction_test(TEST_GEMINI_VIDEO_URL)
    else:
        print(
            "\nℹ️ Skipping Gemini extraction test — set E2E_GEMINI_TEST_URL "
            "to a video URL to enable this step."
        )

    # 1. Sign in using an existing, confirmed Supabase account
    token = do_login(TEST_EMAIL, TEST_PASSWORD)
    print("\n🟢 JWT TOKEN ACQUIRED")

    # 1b. Ensure profile row exists in Supabase `user` table (for DB linkage)
    ensure_user_profile_exists(token, TEST_EMAIL)

    # 2. Create a recipe (writes to Supabase)
    recipe = create_recipe(token, TEST_RECIPE)
    recipe_id = recipe.get("id")
    print("\n🟢 RECIPE STORED:", recipe)

    # 3. List recipes (reads from Supabase)
    recipes = list_recipes(token)
    print("\n🟢 CURRENT RECIPES COUNT:", len(recipes))

    # 4. Add pantry items (upsert)
    add_pantry_item(token, "bread", qty=2, unit="slices")
    add_pantry_item(token, "butter", qty=1, unit="tbsp")
    add_pantry_item(token, "saad", qty=1, unit="tbsp")

    # 5. Check pantry vs recipe (read)
    if recipe_id:
        check = check_recipe(token, recipe_id)
        print("\n🟢 PANTRY CHECK:", check)

    # 6. Grocery recommender (read/compute)
    recs = get_recommendations(token)
    print("\n🟢 FINAL GROCERY RECOMMENDATIONS:\n", recs)

    print("\n==============================================================")
    print("✅ END-TO-END TEST FINISHED")
    print("==============================================================")
