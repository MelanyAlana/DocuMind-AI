from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
VECTORSTORE_DIR = ROOT_DIR / "vectorstore"
UPLOADS_DIR = ROOT_DIR / "uploads"
APP_TITLE = "DocuMind AI"

load_dotenv(ROOT_DIR / ".env")


def ensure_directories() -> None:
    VECTORSTORE_DIR.mkdir(exist_ok=True)
    UPLOADS_DIR.mkdir(exist_ok=True)


def has_api_key() -> bool:
    return bool(os.getenv("COHERE_API_KEY"))


def get_api_key() -> str:
    key = os.getenv("COHERE_API_KEY")
    if not key:
        raise RuntimeError("Falta COHERE_API_KEY. Añádela al archivo .env.")
    return key
