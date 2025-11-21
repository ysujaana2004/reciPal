"""
================================================================================
END-TO-END SYSTEM TEST SCRIPT
================================================================================

This script tests your ENTIRE backend system with REAL logic:

- Real signup/signin
- Real JWT authentication
- Real yt-dlp downloader
- Real Gemini recipe extraction
- Real DB writes (Supabase or SQLite)
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
================================================================================
"""

import requests
import random
import string
import time

BASE = "http://127.0.0.1:8000"

# Use a simple recipe video — adjust if needed
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=yyi55ZrpJ0E"  # scrambled eggs


# ------------------------------------------------------------------------------
# Helper: Generate random email so signup never conflicts
# ------------------------------------------------------------------------------
def random_email():
    return "".join(random.choices(string.ascii_lowercase, k=8)) + "@test.com"


# ------------------------------------------------------------------------------
# STEP 1: SIGN UP
# ------------------------------------------------------------------------------
def do_signup(email, password="123123"):
    print("\n🔵 SIGNING UP...")
    resp = requests.post(
        f"{BASE}/auth/signup",
        params={"email": email, "password": password}
    )
    print("Response:", resp.text)
    resp.raise_for_status()


# ------------------------------------------------------------------------------
# STEP 2: SIGN IN → get JWT token
# ------------------------------------------------------------------------------
def do_signin(email, password="123123"):
    print("\n🔵 SIGNING IN...")
    resp = requests.post(
        f"{BASE}/auth/signin",
        params={"email": email, "password": password}
    )
    print("Response:", resp.text)
    resp.raise_for_status()
    token = resp.json()["access_token"]
    return token


# ------------------------------------------------------------------------------
# STEP 3: EXTRACT A RECIPE VIA REAL DOWNLOADER + GEMINI
# ------------------------------------------------------------------------------
def do_extract_recipe(token, url):
    print("\n🔵 EXTRACTING RECIPE (REAL GEMINI + REAL DOWNLOAD)...")
    resp = requests.post(
        f"{BASE}/recipes/extract",
        params={"url": url},
        headers={"Authorization": f"Bearer {token}"}
    )
    print("Response:", resp.text)
    resp.raise_for_status()
    return resp.json()


# ------------------------------------------------------------------------------
# STEP 4: ADD PANTRY ITEMS
# ------------------------------------------------------------------------------
def add_pantry_item(token, name):
    print(f"\n🔵 ADDING PANTRY ITEM: {name}")
    resp = requests.post(
        f"{BASE}/pantry/add",
        params={"name": name},
        headers={"Authorization": f"Bearer {token}"}
    )
    print("Response:", resp.text)
    resp.raise_for_status()


# ------------------------------------------------------------------------------
# STEP 5: GET GROCERY RECOMMENDATIONS
# ------------------------------------------------------------------------------
def get_recommendations(token):
    print("\n🔵 GETTING GROCERY RECOMMENDATIONS...")
    resp = requests.get(
        f"{BASE}/grocery/recommendations",
        headers={"Authorization": f"Bearer {token}"}
    )
    print("Response:", resp.text)
    resp.raise_for_status()
    return resp.json()


# ------------------------------------------------------------------------------
# MAIN RUNNER
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n==============================================================")
    print("🚀 STARTING END-TO-END SYSTEM TEST")
    print("==============================================================")

    email = random_email()
    password = "123123"

    # 1. Sign up
    do_signup(email, password)

    # 2. Sign in
    token = do_signin(email, password)
    print("\n🟢 JWT TOKEN ACQUIRED")

    # 3. Extract recipe
    recipe = do_extract_recipe(token, TEST_VIDEO_URL)
    print("\n🟢 RECIPE STORED:", recipe)

    # 4. Add pantry items manually
    #    (You can adjust based on the recipe returned)
    add_pantry_item(token, "salt")
    add_pantry_item(token, "eggs")
    add_pantry_item(token, "butter")

    # 5. Grocery recommender
    recs = get_recommendations(token)
    print("\n🟢 FINAL GROCERY RECOMMENDATIONS:\n", recs)

    print("\n==============================================================")
    print("✅ END-TO-END TEST FINISHED")
    print("==============================================================")
