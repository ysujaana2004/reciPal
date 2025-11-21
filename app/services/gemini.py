# app/services/gemini.py
"""
===============================================================================
gemini.py — Extracting Recipes From Audio Using Google's Gemini API
===============================================================================

What this file does (in plain English):

After we download the audio from a video (YouTube, TikTok, IG, etc.),
we need to send that audio file to Google's Gemini AI model so it can
*analyze the spoken words* and extract a structured recipe.

This module provides **one main function**:

    extract_recipe(audio_path: str) -> dict

It performs the following steps:

    1. Read the audio file from disk.
    2. Provide a clear prompt telling Gemini EXACTLY what format we want.
    3. Send the audio + prompt to Gemini’s API.
    4. Receive back a JSON string describing the recipe.
    5. Parse and validate that JSON.
    6. Return a clean Python dictionary.

If anything goes wrong (invalid file, API error, JSON issues), a
descriptive Python exception will be raised.

IMPORTANT:
----------
This function does *not* save anything to the database.
It simply extracts structured recipe data from audio.
===============================================================================
"""

import json
import os

import google.generativeai as genai

from dotenv import load_dotenv
load_dotenv()  # loads .env into the environment


# ---------------------------------------------------------------------------
# Configure Gemini API using environment variable.
# The user must set: GOOGLE_API_KEY=...
# ---------------------------------------------------------------------------
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError(
        "GOOGLE_API_KEY environment variable not set. "
        "Please add it to your .env file."
    )

genai.configure(api_key=api_key)

# Use a model suitable for audio + text extraction
MODEL_NAME = "gemini-2.5-flash"


# ---------------------------------------------------------------------------
# MAIN FUNCTION: extract_recipe
# ---------------------------------------------------------------------------
def extract_recipe(audio_path: str) -> dict:
    """
    Extract a structured recipe from an audio file using Gemini.

    Parameters
    ----------
    audio_path : str
        Full path to the audio file (e.g. .mp3) downloaded by downloader.py

    Returns
    -------
    dict
        {
            "title": str,
            "ingredients": [str, str, ...],
            "instructions": str
        }

    Raises
    ------
    ValueError:
        - If file does not exist
        - If Gemini returns invalid JSON

    RuntimeError:
        - If Gemini API call fails
    """

    # -------------------------------
    # Step 1: Validate input
    # -------------------------------
    if not audio_path or not os.path.exists(audio_path):
        raise ValueError(f"Audio file not found: {audio_path}")

    # -------------------------------
    # Step 2: Read the audio content
    # -------------------------------
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    audio_data = {
        "mime_type": "audio/mp3",
        "data": audio_bytes,
    }

    # -------------------------------
    # Step 3: Construct prompt
    # -------------------------------
    prompt = """
You are a recipe extraction assistant.

Given the audio of someone describing a cooking process,
you MUST extract the recipe into the following STRICT JSON format:

{
  "title": "Name of the recipe",
  "ingredients": [("ingredient one", "ingredient two", ...)],
  "instructions": "Full instructions as a single string."
}

Rules:
- "ingredients" must be a simple list of strings (no quantities, no extra info). I.e. 3 eggs should be just "eggs".
- No extra commentary or text outside the JSON.
- No markdown.
- No backticks.
- Do not guess wildly — only extract what is clearly stated.
"""

    # -------------------------------
    # Step 4: Call Gemini
    # -------------------------------
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(
            [prompt, audio_data]
        )
    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {str(e)}")

    # -------------------------------
    # Step 5: Extract JSON text
    # -------------------------------
    if not hasattr(response, "text") or not response.text:
        raise RuntimeError("Gemini returned empty response.")

    raw_output = response.text.strip()

    # -------------------------------
    # Step 6: Parse JSON
    # -------------------------------
    try:
        data = json.loads(raw_output)
    except Exception:
        raise ValueError(
            "Gemini returned invalid JSON. Raw output:\n" + raw_output
        )

    # -------------------------------
    # Step 7: Validate expected fields
    # -------------------------------
    if not isinstance(data, dict):
        raise ValueError("Gemini response must be a JSON object.")

    if "title" not in data or "ingredients" not in data or "instructions" not in data:
        raise ValueError("Gemini JSON missing required fields.")

    if not isinstance(data["ingredients"], list):
        raise ValueError("`ingredients` must be a list of strings.")

    return data
