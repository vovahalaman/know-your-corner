"""Settings: the only module that reads the environment."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL = "gemini-3.5-flash-lite"
