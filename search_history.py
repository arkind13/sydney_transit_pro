# search_history.py
"""
Persistent search history with favourites — survives browser close & server restart.

Stores last 10 searches + favourites in search_history.json.
"""

import json
import os
from datetime import datetime
from typing import Optional

HISTORY_FILE = "search_history.json"
MAX_HISTORY = 10


# ─────────────────────────────────────────────────────────────────
#  Internal helpers
# ─────────────────────────────────────────────────────────────────

def _load() -> dict:
    """Load the full history dict from JSON. Returns empty dict if file missing."""
    if not os.path.exists(HISTORY_FILE):
        return {"searches": [], "favourites": []}
    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
            # Ensure expected keys exist
            if "searches" not in data:
                data["searches"] = []
            if "favourites" not in data:
                data["favourites"] = []
            return data
    except (json.JSONDecodeError, IOError):
        return {"searches": [], "favourites": []}


def _save(data: dict) -> None:
    """Persist the history dict to JSON."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────

def add_search(origin: str, destination: str) -> None:
    """
    Record a search. Keeps only the last MAX_HISTORY entries.
    Deduplicates: if origin+destination already exists, it moves to top.
    """
    data = _load()

    # Remove duplicate if exists
    data["searches"] = [
        s for s in data["searches"]
        if not (s["origin"] == origin and s["destination"] == destination)
    ]

    # Prepend new entry
    data["searches"].insert(0, {
        "origin": origin,
        "destination": destination,
        "timestamp": datetime.now().isoformat(),
    })

    # Trim to max
    data["searches"] = data["searches"][:MAX_HISTORY]

    _save(data)


def get_recent_searches() -> list[dict]:
    """Return last 10 searches, newest first."""
    return _load()["searches"]


def toggle_favourite(origin: str, destination: str) -> bool:
    """
    Toggle a favourite pair. Returns True if now favourited, False if removed.
    """
    data = _load()
    favs = data["favourites"]

    # Check if already favourited
    for fav in favs:
        if fav["origin"] == origin and fav["destination"] == destination:
            favs.remove(fav)
            _save(data)
            return False

    # Add new favourite
    favs.insert(0, {
        "origin": origin,
        "destination": destination,
        "timestamp": datetime.now().isoformat(),
    })
    _save(data)
    return True


def is_favourite(origin: str, destination: str) -> bool:
    """Check if an origin+destination pair is favourited."""
    data = _load()
    for fav in data["favourites"]:
        if fav["origin"] == origin and fav["destination"] == destination:
            return True
    return False


def get_favourites() -> list[dict]:
    """Return all favourited searches."""
    return _load()["favourites"]
