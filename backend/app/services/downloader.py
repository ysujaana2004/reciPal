# app/services/downloader.py
"""
=========================================================================
downloader.py — Downloading Audio From Online Videos (YouTube, TikTok, etc.)
=========================================================================

What this file does (in plain English):

This file contains the helper function that downloads the audio
from an online video link. The audio is later sent to Gemini for
recipe extraction.

Why we need this:
-----------------
Gemini cannot extract recipes directly from a video URL.
It needs the actual audio data. So we must:

    1. Take a URL (e.g., YouTube, TikTok, Instagram)
    2. Download the audio track locally
    3. Return the path to that temporary audio file

We use "yt-dlp", a powerful library that can:
    - Automatically determine the platform (no need to specify)
    - Extract only the audio
    - Save it to a file we control

What this function returns:
---------------------------
A string containing the file path of the downloaded audio file.
You can then pass this file path directly to Gemini.

If anything goes wrong (invalid URL, network issue, unsupported site),
a descriptive Python exception is raised.
=========================================================================
"""

import os
import uuid
import tempfile
from yt_dlp import YoutubeDL


def download_audio(url: str) -> str:
    """
    Download audio from a given URL using yt-dlp.

    Steps:
    ------
    1. Create a temporary folder for the downloaded file.
    2. Use yt-dlp to download ONLY the audio track.
    3. Save it as <uuid>.mp3 in the temporary directory.
    4. Return the absolute file path.

    Raises:
    -------
    - ValueError: if URL is missing or malformed.
    - RuntimeError: if yt-dlp fails to download the audio.
    """

    if not url or not isinstance(url, str):
        raise ValueError("A valid URL string must be provided.")

    # Create a temporary directory for this download
    temp_dir = tempfile.mkdtemp()
    filename = f"{uuid.uuid4()}.mp3"
    output_path = os.path.join(temp_dir, filename)

    # yt-dlp configuration
    ydl_opts = {
        "format": "bestaudio/best",       # pick highest-quality audio
        "outtmpl": output_path,           # exact output file path
        "quiet": True,                    # silence yt-dlp logs
        "noplaylist": True,               # prevent downloading playlists
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        raise RuntimeError(f"Failed to download audio: {str(e)}")

    # Confirm file exists
    if not os.path.exists(output_path):
        raise RuntimeError("Audio file was not created.")

    return output_path
