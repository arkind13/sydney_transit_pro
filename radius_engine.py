import requests
from config import get_api_key

COORD_URL = "https://api.transport.nsw.gov.au/v1/tp/coord"

def get_stops_within_radius(lat, lng, radius_m=1000):
    """
    Fetches all transit stops within a 1,000m radius using TfNSW Coord API.
    """
    headers = {"Authorization": f"apikey {get_api_key()}"}
    # TfNSW expects LNG:LAT order for the coord parameter
    coord_str = f"{lng}:{lat}:EPSG:4326"
    
    params = {
        "outputFormat": "rapidJSON",
        "coord": coord_str,
        "type": "coord",
        "radius_1": str(radius_m),
        "inclFilter": "1",
        "type_1": "BUS_POINT, TRAIN, METRO, FERRY"
    }
    
    response = requests.get(COORD_URL, headers=headers, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    stops = []
    for loc in data.get("locations", []):
        stops.append({
            "stop_id": loc.get("id"),
            "stop_name": loc.get("name"),
            "lat": loc.get("coord")[1],
            "lng": loc.get("coord")[0],
            "transport_type": (loc.get("productClasses") or ["Unknown"])[0]
        })
    return stops