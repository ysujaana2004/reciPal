# tests/test_gemini.py
"""
Tests for gemini.py

These tests verify:
- Input validation (missing file)
- Proper Gemini API invocation
- Correct JSON parsing
- Handling of malformed JSON

We fully MOCK the Gemini API to avoid real network calls.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from app.services.gemini import extract_recipe


# -------------------------------------------------------------------
# TEST: Missing or nonexistent file
# -------------------------------------------------------------------
def test_extract_recipe_missing_file():
    with pytest.raises(ValueError):
        extract_recipe("not_a_real_file.mp3")


# -------------------------------------------------------------------
# TEST: Successful extraction (mock Gemini)
# -------------------------------------------------------------------
@patch("app.services.gemini.genai.GenerativeModel")
def test_extract_recipe_success(mock_model_cls):
    """
    We simulate Gemini returning valid JSON.
    """

    # Create a real temp audio file
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "audio.mp3")
    with open(audio_path, "wb") as f:
        f.write(b"fake audio")

    # Mock Gemini model instance
    mock_model = MagicMock()
    mock_model_cls.return_value = mock_model

    # Mock the Gemini response object
    mock_response = MagicMock()
    mock_response.text = """
    {
      "title": "Pasta",
      "ingredients": ["pasta", "salt"],
      "instructions": "Boil pasta. Add salt."
    }
    """
    mock_model.generate_content.return_value = mock_response

    data = extract_recipe(audio_path)

    assert data["title"] == "Pasta"
    assert data["ingredients"] == ["pasta", "salt"]
    assert "Boil pasta" in data["instructions"]


# -------------------------------------------------------------------
# TEST: Gemini returns malformed JSON
# -------------------------------------------------------------------
@patch("app.services.gemini.genai.GenerativeModel")
def test_extract_recipe_bad_json(mock_model_cls):
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "audio.mp3")
    with open(audio_path, "wb") as f:
        f.write(b"fake audio")

    mock_model = MagicMock()
    mock_model_cls.return_value = mock_model

    mock_response = MagicMock()
    mock_response.text = "this is not json"
    mock_model.generate_content.return_value = mock_response

    with pytest.raises(ValueError):
        extract_recipe(audio_path)
