# test_gemini_recipe_flow.py
"""
Standalone integration tester: download audio, extract recipe via Gemini,
and persist it via the /recipes API (same flow as end_to_end_test).

WARNING:
    - Requires a running backend server (default http://127.0.0.1:8000)
    - Needs GOOGLE_API_KEY, Supabase creds, and yt-dlp installed
    - Uses a real video URL from E2E_GEMINI_TEST_URL
    - Hits the real /auth and /recipes endpoints

Configure via env vars (dotenv supported):
    E2E_GEMINI_TEST_URL   -> Video URL to download and transcribe
    E2E_TEST_EMAIL        -> Supabase login email (falls back to TEST_EMAIL const)
    E2E_TEST_PASSWORD     -> Supabase login password (falls back to TEST_PASSWORD)
    E2E_BASE_URL          -> Override API base URL (default http://127.0.0.1:8000)

Run it just like `python end_to_end_test.py`:

    python test_gemini_recipe_flow.py
"""

import json
import os
import shutil
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from app.services.downloader import download_audio
from app.services.gemini import extract_recipe


load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
VIDEO_URL = "https://www.youtube.com/watch?v=9Mpk5pdYAf0"
TEST_EMAIL = "shadwking58@gmail.com"
TEST_PASSWORD = "password"


def _login(email: str, password: str) -> str:
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"},
    )
    resp.raise_for_status()
    token = resp.json().get("access_token")
    if not token:
        raise RuntimeError("Login succeeded but no access token returned.")
    return token


def _create_recipe(token: str, recipe_payload: dict) -> dict:
    resp = requests.post(
        f"{BASE_URL}/recipes/",
        json=recipe_payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    resp.raise_for_status()
    return resp.json()


def _list_recipes(token: str) -> list:
    resp = requests.get(
        f"{BASE_URL}/recipes/",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp.raise_for_status()
    return resp.json()


def main():
    if not VIDEO_URL:
        raise SystemExit(
            "E2E_GEMINI_TEST_URL is not set. Export it to a video URL before running."
        )

    print("\n==============================================================")
    print("🚀 STARTING GEMINI RECIPE FLOW TEST")
    print("==============================================================")

    token = _login(TEST_EMAIL, TEST_PASSWORD)
    print("🟢 Logged in successfully")

    audio_path = None
    try:
        print("🔵 Downloading audio...")
        audio_path = download_audio(VIDEO_URL)
        print(f"Audio saved to: {audio_path}")

        print("🔵 Extracting recipe via Gemini...")
        recipe = extract_recipe(audio_path)
    finally:
        if audio_path:
            shutil.rmtree(Path(audio_path).parent, ignore_errors=True)

    if not recipe.get("title"):
        raise RuntimeError("Gemini response missing title")
    if not recipe.get("ingredients"):
        raise RuntimeError("Gemini response missing ingredients")
    if not recipe.get("instructions"):
        raise RuntimeError("Gemini response missing instructions")

    unique_title = f"{recipe['title']} (gemini-flow {int(time.time())})"
    payload = {
        "title": unique_title,
        "ingredients": recipe["ingredients"],
        "instructions": recipe["instructions"],
        "source_url": VIDEO_URL,
    }

    print("🔵 Storing recipe via /recipes ...")
    created = _create_recipe(token, payload)
    if not created.get("id"):
        raise RuntimeError("Recipe creation response missing id")
    if created.get("title") != unique_title:
        raise RuntimeError("Recipe creation response returned unexpected title")

    recipes = _list_recipes(token)
    titles = [r.get("title") for r in recipes]
    if unique_title not in titles:
        raise RuntimeError("Stored recipes does not include the Gemini recipe")

    print("\n🟢 Gemini recipe saved!")
    print(json.dumps(created, indent=2))
    print("\n==============================================================")
    print("✅ GEMINI RECIPE FLOW TEST FINISHED")
    print("==============================================================")


if __name__ == "__main__":
    main()
