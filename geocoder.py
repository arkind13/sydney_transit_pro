# geocoder.py
"""
Three-tier geocoding:
  1. Station dictionary (instant, free, 95%+ hit rate)
  2. Google Geocoding API (reliable, pay-as-you-go)
  3. Nominatim / OpenStreetMap (free backup)
"""

import re
import time
import os
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from station_lookup import find_station_coords, get_station_name

# ─────────────────────────────────────────────────────────────────
#  Module-level tracking of which tier was last used
# ─────────────────────────────────────────────────────────────────
_last_geocode_source: str = "unknown"


# ─────────────────────────────────────────────────────────────────
#  Google Geocoding API key
# ─────────────────────────────────────────────────────────────────
def _get_google_key() -> str:
    """
    Load Google API key from:
      1. Streamlit secrets (.streamlit/secrets.toml or Cloud dashboard)
      2. Environment variable
    """
    try:
        import streamlit as st
        key = st.secrets.get("GOOGLE_GEOCODING_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    return os.getenv("GOOGLE_GEOCODING_API_KEY", "")


# ─────────────────────────────────────────────────────────────────
#  Nominatim locator (last-resort fallback)
# ─────────────────────────────────────────────────────────────────
_nominatim = Nominatim(
    user_agent="SydneyTransitPro_v3",
    timeout=10,
)


def clean_address(address: str) -> str:
    """Remove unit/level/suite numbers to improve geocoding accuracy."""
    cleaned = re.sub(
        r'\b(Unit|Level|Suite|Apt|Apartment)\s+\d+\s*/\s*',
        '',
        address,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r'^(Unit|Level|Suite|Apt|Apartment)\s+\d+[\s,]*',
        '',
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r'^\d+\s*/\s*', '', cleaned)
    return cleaned.strip()


# ─────────────────────────────────────────────────────────────────
#  Google Geocoding
# ─────────────────────────────────────────────────────────────────
def _google_geocode(query: str) -> tuple:
    """
    Call Google Geocoding API.
    Returns (lat, lng, formatted_address) or (None, None, None).
    """
    key = _get_google_key()
    if not key:
        return None, None, None

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": query,
        "region": "au",
        "components": "country:AU",
        "key": key,
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        if data.get("status") == "OK" and data.get("results"):
            result = data["results"][0]
            loc = result["geometry"]["location"]
            return loc["lat"], loc["lng"], result.get("formatted_address", query)

    except Exception:
        pass

    return None, None, None


# ─────────────────────────────────────────────────────────────────
#  Nominatim fallback
# ─────────────────────────────────────────────────────────────────
def _nominatim_geocode(query: str, attempt: int = 1, max_attempts: int = 2) -> tuple:
    """Last-resort fallback using OSM Nominatim."""
    lower_q = query.lower()
    if "nsw" in lower_q:
        full_query = f"{query}, Australia"
    elif "sydney" in lower_q:
        full_query = f"{query}, NSW, Australia"
    else:
        full_query = f"{query}, Sydney NSW, Australia"

    try:
        location = _nominatim.geocode(full_query, exactly_one=True)
        if location:
            return location.latitude, location.longitude, location.address
    except (GeocoderTimedOut, GeocoderServiceError):
        if attempt <= max_attempts:
            time.sleep(1)
            return _nominatim_geocode(query, attempt + 1, max_attempts)

    return None, None, None


# ─────────────────────────────────────────────────────────────────
#  MAIN PUBLIC FUNCTION — three-tier geocoding
# ─────────────────────────────────────────────────────────────────
def get_coordinates(query: str) -> tuple:
    """
    Three-tier geocoding:
      1. Station dictionary  → instant, free
      2. Google Geocoding    → reliable, paid
      3. Nominatim           → free backup

    Returns (latitude, longitude, display_name) or (None, None, None).
    """
    global _last_geocode_source

    if not query or not query.strip():
        _last_geocode_source = "empty_query"
        return None, None, None

    # ── Tier 1: Station dictionary ──────────────────────────────
    coords = find_station_coords(query)
    if coords:
        _last_geocode_source = "station_dictionary"
        name = get_station_name(query) or query
        return coords[0], coords[1], name

    # ── Tier 2: Google Geocoding ────────────────────────────────
    lat, lng, addr = _google_geocode(query)
    if lat is not None and lng is not None:
        _last_geocode_source = "google_api"
        return lat, lng, addr

    # ── Tier 3: Nominatim fallback ──────────────────────────────
    _last_geocode_source = "nominatim_fallback"
    return _nominatim_geocode(query)


# ─────────────────────────────────────────────────────────────────
#  API status & tracking helpers
# ─────────────────────────────────────────────────────────────────
# geocoder.py — replace the ping_google() function at the bottom

# Cache for ping_google to avoid hitting API on every render
_ping_cache: dict = {"timestamp": 0.0, "result": None}
_PING_CACHE_TTL: float = 300.0  # 5 minutes


def ping_google() -> dict:
    """
    Test if Google Geocoding API is reachable.
    Cached for 5 minutes to avoid wasting quota on every Streamlit rerender.
    Returns: {"success": bool, "message": str}
    """
    global _ping_cache
    now = time.time()

    # Return cached result if still fresh
    if (now - _ping_cache["timestamp"]) < _PING_CACHE_TTL and _ping_cache["result"] is not None:
        return _ping_cache["result"]

    # ── Fresh call ────────────────────────────────────────────
    key = _get_google_key()
    if not key:
        result = {"success": False, "message": "No API key configured"}
        _ping_cache = {"timestamp": now, "result": result}
        return result

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": "Sydney NSW",
        "region": "au",
        "key": key,
    }

    try:
        r = requests.get(url, params=params, timeout=8)
        data = r.json()
        status = data.get("status", "")
        if status == "OK":
            result = {"success": True, "message": "Connected"}
        elif status == "REQUEST_DENIED":
            result = {"success": False, "message": "API key denied — check console"}
        elif status == "OVER_QUERY_LIMIT":
            result = {"success": False, "message": "Quota exceeded"}
        else:
            result = {"success": False, "message": f"Error: {status}"}
    except Exception as e:
        result = {"success": False, "message": f"Timeout: {str(e)[:40]}"}

    _ping_cache = {"timestamp": now, "result": result}
    return result
