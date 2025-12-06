# tests/test_downloader_real.py
"""
Real download test for downloader.py

WARNING:
--------
This test performs an actual network request using yt-dlp.

Use only for local development, NOT for CI/CD pipelines,
because:
  - it requires internet
  - it is slow
  - YouTube may rate-limit or remove the video someday

This test validates:
  - A real URL downloads successfully
  - The output audio file exists
  - The file is not empty
"""

import os
import shutil
from app.services.downloader import download_audio


def test_download_audio_real():
    # This is a tiny, public-domain reference video commonly used in testing.
    url = "https://www.youtube.com/watch?v=9Mpk5pdYAf0"

    # Download the audio
    path = download_audio(url)

    try:
        # File should exist
        assert os.path.exists(path), "Downloaded file does not exist."

        # File should not be empty
        assert os.path.getsize(path) > 0, "Downloaded file is empty."

    finally:
        # Cleanup: remove entire temp directory
        temp_dir = os.path.dirname(path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)