from typing import List, NamedTuple
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError

class GeoPoint(NamedTuple):
    lat: float
    lng: float
    display_name: str

def geocode_address_options(query: str, limit: int = 5) -> List[GeoPoint]:
    """
    Translates a query into multiple Sydney-biased coordinate options.
    """
    geolocator = Nominatim(user_agent="sydney_transit_pro_v1")
    
    # Biasing search to Sydney, NSW to avoid global naming conflicts
    sydney_query = f"{query}, Sydney, NSW, Australia"
    
    try:
        locations = geolocator.geocode(sydney_query, exactly_one=False, limit=limit, timeout=10)
        
        if not locations:
            return []
            
        return [
            GeoPoint(lat=loc.latitude, lng=loc.longitude, display_name=loc.address)
            for loc in locations
        ]
    except GeopyError as e:
        raise ConnectionError(f"Geocoding service unavailable: {e}")