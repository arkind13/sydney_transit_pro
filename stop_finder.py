import requests
from config import get_api_key

STOP_FINDER_URL = "https://api.transport.nsw.gov.au/v1/tp/stop_finder"

def ping_api() -> dict:
    """
    Sends an authenticated request to TfNSW to confirm the API key is valid[cite: 3].
    """
    headers = {"Authorization": f"apikey {get_api_key() or ''}"}
    params = {
        "outputFormat": "rapidJSON",
        "type_sf": "stop",
        "name_sf": "Central",
        "TFNSWTR": "true"
    }

    try:
        response = requests.get(STOP_FINDER_URL, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return {"success": True, "message": "TfNSW API: Connected"}
        return {"success": False, "message": f"API Error: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"Connection error: {str(e)}"}