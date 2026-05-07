# gps_utils.py
from typing import Optional, Tuple
import streamlit as st

def get_live_gps(
    mode: str = "manual",
    manual_lat: Optional[float] = None,
    manual_lng: Optional[float] = None
) -> Tuple[float, float]:
    """
    Returns (lat, lng).
    Use mode="manual" for testing, or "browser" for real GPS.
    """
    if mode == "manual":
        if manual_lat is None or manual_lng is None:
            return (-33.7696, 150.8198)   # Mount Druitt Station
        return (manual_lat, manual_lng)

    if mode == "browser":
        try:
            from streamlit_js_eval import get_geolocation
            location = get_geolocation()
            if location and "coords" in location:
                return (
                    location["coords"]["latitude"],
                    location["coords"]["longitude"]
                )
        except Exception:
            pass
        # Fallback
        return (-33.7696, 150.8198)

    # Ultimate fallback
    return (-33.7696, 150.8198)