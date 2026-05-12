# trip_planner.py
import requests
from datetime import datetime
import pytz
from config import get_api_key

BASE_URL = "https://api.transport.nsw.gov.au/v1/tp"
SYDNEY_TZ = pytz.timezone("Australia/Sydney")

def _syd_now():
    return SYDNEY_TZ.localize(datetime.now())

def parse_to_sydney_time(dt_str):
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        return dt.astimezone(SYDNEY_TZ)
    except Exception:
        return None

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

    # Corrected: changed 'not_id' to 'dest_id'
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
            summary_parts = []

            total_seconds = journey.get("duration", 0) or journey.get("totalDuration", 0)
            if not total_seconds:
                total_seconds = sum(leg.get("duration", 0) for leg in journey.get("legs", []))

            total_minutes = total_seconds // 60

            for leg in journey.get("legs", []):
                transport = leg.get("transportation", {})
                mode_class = transport.get("product", {}).get("class")
                
                ui_mode = "TRAIN" if mode_class == 1 else "BUS" if mode_class == 5 else "WALK"
                
                mode_name = transport.get('name', 'Walk')
                dest_name = leg["destination"]["name"]
                
                if ui_mode == "WALK":
                    # Corrected key access for distance
                    walk_dist = leg.get("properties", {}).get("distance", "0")
                    summary_parts.append(f"Walk for {walk_dist}m")
                else:
                    summary_parts.append(f"{mode_name} to {dest_name}")

                bundle = {
                    "mode": ui_mode,
                    "action": transport.get('disassembledName', mode_name),
                    "origin": leg["origin"]["name"],
                    "destination": dest_name,
                    "duration_min": leg.get("duration", 0) // 60,
                    "stops": []
                }

                for stop in leg.get("stopSequence", []):
                    arr_time = parse_to_sydney_time(stop.get("arrivalTimePlanned", "")[:19])
                    bundle["stops"].append({
                        "name": stop.get("name"),
                        "planned_arrival": arr_time.strftime("%H:%M") if arr_time else "",
                        "lat": stop.get("coord", [0, 0])[0],
                        "lng": stop.get("coord", [0, 0])[1]
                    })
                leg_bundles.append(bundle)

            dep_time = parse_to_sydney_time(journey["legs"][0]["origin"]["departureTimePlanned"][:19])
            arr_time = parse_to_sydney_time(journey["legs"][-1]["destination"]["arrivalTimePlanned"][:19])

            parsed_options.append({
                "depart": dep_time.strftime("%H:%M") if dep_time else "",
                "arrive": arr_time.strftime("%H:%M") if arr_time else "",
                "duration": f"{total_minutes} min",
                "total_minutes": total_minutes,
                "changes": len(journey["legs"]) - 1,
                "leg_bundles": leg_bundles,
                "journey_summary": " → ".join(summary_parts),
                "route_description": (
                    f"{journey['legs'][0]['origin']['name']} to "
                    f"{journey['legs'][-1]['destination']['name']}"
                )
            })
        return parsed_options
    except Exception:
        return []
