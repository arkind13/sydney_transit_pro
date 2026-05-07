from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import re
import time

# Use one global locator with the hardened settings
locator = Nominatim(
    user_agent="SydneyTransitPro_User_Abdul_v2", 
    timeout=10
)

def clean_address(address: str) -> str:
    """
    Removes unit/level/suite numbers to improve geocoding accuracy.
    """
    cleaned = re.sub(
        r'\b(Unit|Level|Suite|Apt|Apartment)\s+\d+\s*/\s*',
        '',
        address,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r'^(Unit|Level|Suite|Apt|Apartment)\s+\d+[\s,]*',
        '',
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(r'^\d+\s*/\s*', '', cleaned)
    return cleaned.strip()

def get_coordinates(query: str, attempt=1, max_attempts=3):
    """
    Geocodes a cleaned address with a retry mechanism for cloud stability.
    """
    cleaned_query = clean_address(query)

    # Context hardening for Sydney
    lower_q = cleaned_query.lower()
    if "nsw" in lower_q:
        full_query = f"{cleaned_query}, Australia"
    elif "sydney" in lower_q:
        full_query = f"{cleaned_query}, NSW, Australia"
    else:
        full_query = f"{cleaned_query}, Sydney NSW, Australia"

    try:
        # IMPORTANT: Use the global 'locator' here, not a new one
        location = locator.geocode(full_query, exactly_one=True)
        if location:
            return location.latitude, location.longitude, location.address
        return None, None, None

    except (GeocoderTimedOut, GeocoderServiceError):
        # If the cloud times out, wait 1 second and try again
        if attempt <= max_attempts:
            time.sleep(1)
            return get_coordinates(query, attempt + 1, max_attempts)
        return None, None, None
