```python
# journey_state.py
from dataclasses import dataclass
from typing import Optional, Dict
import datetime
from zoneinfo import ZoneInfo

SYDNEY_TZ = ZoneInfo("Australia/Sydney")

@dataclass
class JourneyState:
    status: str = "IDLE"
    destination: Optional[str] = None
    active_route: Optional[Dict] = None
    start_time: Optional[datetime.datetime] = None
    max_stop_index: int = -1

def initialise_state() -> JourneyState:
    return JourneyState()

def start_journey(state: JourneyState, origin_gps: tuple, destination: str, active_route: dict) -> JourneyState:
    state.status = "ACTIVE"
    state.destination = destination
    state.active_route = active_route
    state.start_time = datetime.datetime.now(SYDNEY_TZ)
    state.max_stop_index = -1
    return state

def complete_journey(state: JourneyState) -> JourneyState:
    state.status = "IDLE"
    state.max_stop_index = -1
    return state
```

```python
# trip_planner.py
import os
import time

os.environ['TZ'] = 'Australia/Sydney'
try:
    time.tzset()
except AttributeError:
    pass

import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from config import get_api_key

BASE_URL = "https://api.transport.nsw.gov.au/v1/tp"
SYDNEY_TZ = ZoneInfo("Australia/Sydney")


def _syd_now():
    return datetime.now(SYDNEY_TZ)


def find_stop_id(search_text: str):
    headers = {"Authorization": f"apikey {get_api_key() or ''}"}
    params = {
        "outputFormat": "rapidJSON",
        "type_sf": "any",
        "name_sf": search_text,
        "anyMaxSizeHitList": 1,
        "TFNSWTR": "true"
    }
    try:
        r = requests.get(f"{BASE_URL}/stop_finder", headers=headers, params=params, timeout=18)
        r.raise_for_status()
        locations = r.json().get("locations", [])
        return locations[0].get("id") if locations else None
    except Exception:
        return None


def get_real_journey_options(origin: str, destination: str):
    headers = {"Authorization": f"apikey {get_api_key() or ''}"}
    origin_id = find_stop_id(origin)
    dest_id = find_stop_id(destination)

    if not origin_id or not dest_id:
        return []

    now_syd = _syd_now()

    params = {
        "outputFormat": "rapidJSON",
        "coordOutputFormat": "EPSG:4326",
        "depArrMacro": "dep",
        "itdDate": now_syd.strftime("%Y%m%d"),
        "itdTime": now_syd.strftime("%H%M"),
        "type_origin": "any",
        "name_origin": origin_id,
        "type_destination": "any",
        "name_destination": dest_id,
        "calcNumberOfTrips": 3,
        "includeRealtime": "true",
        "version": "10.2.1.42"
    }

    try:
        r = requests.get(f"{BASE_URL}/trip", headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()

        parsed_options = []
        for journey in data.get("journeys", []):
            leg_bundles = []

            total_seconds = journey.get("duration", 0)

            if not total_seconds:
                total_seconds = journey.get("totalDuration", 0)

            if not total_seconds:
                total_seconds = sum(
                    leg.get("duration", 0)
                    for leg in journey.get("legs", [])
                )

            if not total_seconds:
                try:
                    dep_str = journey["legs"][0]["origin"]["departureTimePlanned"]
                    arr_str = journey["legs"][-1]["destination"]["arrivalTimePlanned"]
                    dep_dt = datetime.strptime(dep_str[:19], "%Y-%m-%dT%H:%M:%S")
                    arr_dt = datetime.strptime(arr_str
