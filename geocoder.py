from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import re
import time

# GLOBAL locator with high timeout for Cloud stability
locator = Nominatim(
    user_agent="SydneyTransitPro_Final_Deploy", 
    timeout=10
)

def clean_address(address: str) -> str:
    """Removes unit/level/suite numbers (YOUR ORIGINAL LOGIC)"""
    cleaned = re.sub(r'\b(Unit|Level|Suite|Apt|Apartment)\s+\d+\s*/\s*', '', address, flags=re.IGNORECASE)
    cleaned = re.sub(r'^(Unit|Level|Suite|Apt|Apartment)\s+\d+[\s,]*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^\d+\s*/\s*', '', cleaned)
    return cleaned.strip()

def get_coordinates(query: str, attempt=1, max_attempts=3):
    """Geocodes with YOUR Sydney hardening + Cloud Retry logic"""
    cleaned_query = clean_address(query)
    lower_q = cleaned_query.lower()

    # YOUR ORIGINAL Sydney hardening logic
    if "nsw" in lower_q:
        full_query = f"{cleaned_query}, Australia"
    elif "sydney" in lower_q:
        full_query = f"{cleaned_query}, NSW, Australia"
    else:
        full_query = f"{cleaned_query}, Sydney NSW, Australia"

    try:
        # USE THE GLOBAL LOCATOR (Avoids the timeout error)
        location = locator.geocode(full_query, exactly_one=True)
        if location:
            return location.latitude, location.longitude, location.address
        return None, None, None

    except (GeocoderTimedOut, GeocoderServiceError):
        # Retry logic specifically for Streamlit Cloud stability
        if attempt <= max_attempts:
            time.sleep(1)
            return get_coordinates(query, attempt + 1, max_attempts)
        return None, None, None
