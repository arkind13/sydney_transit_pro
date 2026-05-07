from geopy.geocoders import Nominatim
# Add a unique user_agent and increase the timeout to 10s
locator = Nominatim(
    user_agent="SydneyTransitPro_User_Abdul", 
    timeout=10
)
import re

def clean_address(address: str) -> str:
    """
    Removes unit/level/suite numbers to improve geocoding accuracy.
    Handles: 'Unit 14/37 O\'Riordan St' → '37 O\'Riordan St'
             'Unit 5, 12 Main St'       → '12 Main St'
             '5/10 George St'           → '10 George St'
    """
    # Step 1: 'Unit X/Y' or 'Level X/Y' → keep Y (the street number after slash)
    cleaned = re.sub(
        r'\b(Unit|Level|Suite|Apt|Apartment)\s+\d+\s*/\s*',
        '',
        address,
        flags=re.IGNORECASE
    )
    # Step 2: 'Unit X,' or 'Unit X ' at start → remove entirely
    cleaned = re.sub(
        r'^(Unit|Level|Suite|Apt|Apartment)\s+\d+[\s,]*',
        '',
        cleaned,
        flags=re.IGNORECASE
    )
    # Step 3: Bare 'X/Y ' prefix (no unit word) → keep Y
    cleaned = re.sub(r'^\d+\s*/\s*', '', cleaned)
    
    return cleaned.strip()


def get_coordinates(query: str):
    """
    Geocodes a cleaned address, restricted to Sydney, Australia.
    Returns: (latitude, longitude, display_name)
    """
    geolocator = Nominatim(user_agent="sydney_transit_pro_v3")
    cleaned_query = clean_address(query)

    # Avoid doubling 'NSW' or 'Sydney' if already present in the address
    lower_q = cleaned_query.lower()
    if "nsw" in lower_q:
        full_query = f"{cleaned_query}, Australia"
    elif "sydney" in lower_q:
        full_query = f"{cleaned_query}, NSW, Australia"
    else:
        full_query = f"{cleaned_query}, Sydney NSW, Australia"

    location = geolocator.geocode(full_query, exactly_one=True)

    if location:
        return location.latitude, location.longitude, location.address
    return None, None, None
