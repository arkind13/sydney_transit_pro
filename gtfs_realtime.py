# gtfs_realtime.py
import requests
from google.transit import gtfs_realtime_pb2
from config import get_api_key

# Use v1 (more reliable) — change to v2 only if v1 stops working
GTFS_RT_URL = "https://api.transport.nsw.gov.au/v1/gtfs/realtime/sydneytrains"

def get_trip_delays():
    """Fetch real-time delays from TfNSW. Returns {} on any failure."""
    try:
        headers = {"Authorization": f"apikey {get_api_key()}"}
        
        response = requests.get(GTFS_RT_URL, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return {}   # Silently fail instead of crashing the thread
        
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        delays = {}
        for entity in feed.entity:
            if entity.HasField("trip_update"):
                trip_id = entity.trip_update.trip.trip_id
                for stu in entity.trip_update.stop_time_update:
                    if stu.HasField("departure"):
                        delays[trip_id] = stu.departure.delay
                        break
        
        return delays
        
    except Exception:
        # Any error (bad key, network, parsing, etc.) → return empty
        return {}