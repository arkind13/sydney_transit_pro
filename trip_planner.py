import requests
from datetime import datetime
from config import get_api_key

BASE_URL = "https://api.transport.nsw.gov.au/v1/tp"


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
    except:
        return None


def get_real_journey_options(origin: str, destination: str):
    headers = {"Authorization": f"apikey {get_api_key() or ''}"}
    origin_id = find_stop_id(origin)
    dest_id = find_stop_id(destination)

    if not origin_id or not dest_id:
        return []

    params = {
        "outputFormat": "rapidJSON",
        "coordOutputFormat": "EPSG:4326",
        "depArrMacro": "dep",
        "itdDate": datetime.now().strftime("%Y%m%d"),
        "itdTime": datetime.now().strftime("%H%M"),
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

            # ── FIX: Try multiple duration sources ──────────────────
            total_seconds = journey.get("duration", 0)

            # Fallback 1: some API versions use "totalDuration"
            if not total_seconds:
                total_seconds = journey.get("totalDuration", 0)

            # Fallback 2: sum leg durations ourselves
            if not total_seconds:
                total_seconds = sum(
                    leg.get("duration", 0)
                    for leg in journey.get("legs", [])
                )

            # Fallback 3: calculate from departure/arrival times
            if not total_seconds:
                try:
                    dep_str = journey["legs"][0]["origin"]["departureTimePlanned"]
                    arr_str = journey["legs"][-1]["destination"]["arrivalTimePlanned"]
                    dep_dt = datetime.strptime(dep_str[:19], "%Y-%m-%dT%H:%M:%S")
                    arr_dt = datetime.strptime(arr_str[:19], "%Y-%m-%dT%H:%M:%S")
                    total_seconds = int((arr_dt - dep_dt).total_seconds())
                except Exception:
                    total_seconds = 0

            total_minutes = total_seconds // 60
            # ────────────────────────────────────────────────────────

            for leg in journey.get("legs", []):
                transport = leg.get("transportation", {})
                mode_class = transport.get("product", {}).get("class")
                ui_mode = (
                    "TRAIN" if mode_class == 1
                    else "BUS" if mode_class == 5
                    else "WALK"
                )

                bundle = {
                    "mode": ui_mode,
                    "action": transport.get(
                        'disassembledName',
                        transport.get('name', 'Walk')
                    ),
                    "origin": leg["origin"]["name"],
                    "destination": leg["destination"]["name"],
                    "duration_min": leg.get("duration", 0) // 60,
                    "stops": []
                }

                # Capture coordinates for GPS tracking
                stop_sequence = leg.get("stopSequence", [])
                for stop in stop_sequence:
                    bundle["stops"].append({
                        "name": stop.get("name"),
                        "planned_arrival": stop.get("arrivalTimePlanned", "")[-9:-4],
                        "lat": stop.get("coord", [0, 0])[0],
                        "lng": stop.get("coord", [0, 0])[1]
                    })

                leg_bundles.append(bundle)

            parsed_options.append({
                "depart": journey["legs"][0]["origin"]["departureTimePlanned"][-9:-4],
                "arrive": journey["legs"][-1]["destination"]["arrivalTimePlanned"][-9:-4],
                "duration": f"{total_minutes} min",
                "total_minutes": total_minutes,
                "changes": len(journey["legs"]) - 1,
                "leg_bundles": leg_bundles,
                "route_description": (
                    f"{journey['legs'][0]['origin']['name']} to "
                    f"{journey['legs'][-1]['destination']['name']}"
                )
            })
        return parsed_options
    except:
        return []
