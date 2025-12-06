# tests/test_downloader.py
"""
Tests for downloader.py

These tests verify:
- URL validation
- Temporary file creation
- Proper handling of yt-dlp failures
- Function returns a valid file path

We mock yt-dlp so tests do NOT download real files.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from app.services.downloader import download_audio


# -------------------------------------------------------------------
# TEST: Invalid URL should raise ValueError
# -------------------------------------------------------------------
def test_download_audio_invalid_url():
    with pytest.raises(ValueError):
        download_audio(None)

    with pytest.raises(ValueError):
        download_audio("")


# -------------------------------------------------------------------
# TEST: Successful download (yt-dlp mocked)
# -------------------------------------------------------------------
@patch("app.services.downloader.YoutubeDL")
def test_download_audio_success(mock_yt):
    # Mock instance returned by YoutubeDL(...)
    ydl_instance = MagicMock()
    mock_yt.return_value.__enter__.return_value = ydl_instance

    # Define a fake download that writes the file exactly like yt-dlp would.
    def fake_download(_):
        # yt-dlp receives outtmpl exactly as output_path
        outtmpl = mock_yt.call_args[0][0]["outtmpl"]

        os.makedirs(os.path.dirname(outtmpl), exist_ok=True)
        with open(outtmpl, "wb") as f:
            f.write(b"fake audio data")

    ydl_instance.download.side_effect = fake_download

    # Call real function
    path = download_audio("https://example.com/video")

    # Assertions
    assert os.path.exists(path)
    assert path.endswith(".mp3")


# -------------------------------------------------------------------
# TEST: yt-dlp raises an exception → download_audio wraps it
# -------------------------------------------------------------------
@patch("app.services.downloader.YoutubeDL")
def test_download_audio_failure(mock_yt):
    mock_yt.return_value.__enter__.return_value.download.side_effect = Exception("yt-dlp error")

    with pytest.raises(RuntimeError) as exc:
        download_audio("https://example.com/video")

    assert "Failed to download audio" in str(exc.value)
