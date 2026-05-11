import pytz
import requests
from datetime import timezone
from config import get_api_key

BASE_URL = "https://api.transport.nsw.gov.au/v1/tp"

def find_stop_id(search_text: str):
    headers = {"Authorization": f"apikey {get_api_key()}", "Accept": "application/json"}
    params = {"outputFormat": "rapidJSON", "type_sf": "any",
              "name_sf": search_text, "anyMaxSizeHitList": 1, "TFNSWTR": "true"}
    r = requests.get(f"{BASE_URL}/stop_finder", headers=headers, params=params, timeout=18)
    r.raise_for_status()
    locs = r.json().get("locations", [])
    return locs[0]["id"] if locs else None

def get_real_journey_options(origin: str, destination: str):
    origin_id, dest_id = find_stop_id(origin), find_stop_id(destination)
    if not origin_id or not dest_id: return []

    syd = pytz.timezone("Australia/Sydney")
    now_syd = datetime.now(syd)

    headers = {"Authorization": f"apikey {get_api_key()}", "Accept": "application/json"}
    params = {"outputFormat": "rapidJSON", "coordOutputFormat": "EPSG:4326",
              "depArrMacro": "dep",
              "itdDate": now_syd.strftime("%Y%m%d"),
              "itdTime": now_syd.strftime("%H%M"),
              "type_origin": "any", "name_origin": origin_id,
              "type_destination": "any", "name_destination": dest_id,
              "calcNumberOfTrips": 3, "includeRealtime": "true",
              "version": "10.2.1.42"}

    r = requests.get(f"{BASE_URL}/trip", headers=headers, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    options = []
    for j in data.get("journeys", []):
        total_s = j.get("duration") or sum(leg.get("duration", 0) for leg in j.get("legs", []))
        leg_bundles = []

        for leg in j.get("legs", []):
            transport = leg.get("transportation", {})
            pc = transport.get("product", {}).get("class", -1)
            mode = "TRAIN" if pc == 1 else "BUS" if pc == 5 else "WALK"
            bundle = {"mode": mode,
                      "action": transport.get("disassembledName") or transport.get("name") or "Walk",
                      "origin": leg["origin"]["name"],
                      "destination": leg["destination"]["name"],
                      "duration_min": leg.get("duration", 0) // 60,
                      "stops": [{"name": s["name"],
                                 "planned_arrival": s.get("arrivalTimePlanned", "")[-9:-4],
                                 "lat": s["coord"][0], "lng": s["coord"][1]}
                                for s in leg.get("stopSequence", [])]}
            leg_bundles.append(bundle)

        options.append({"depart": j["legs"][0]["origin"]["departureTimePlanned"][-9:-4],
                        "arrive": j["legs"][-1]["destination"]["arrivalTimePlanned"][-9:-4],
                        "duration": f"{total_s//60} min",
                        "total_minutes": total_s // 60,
                        "changes": len(j["legs"]) - 1,
                        "leg_bundles": leg_bundles,
                        "route_description": f"{j['legs'][0]['origin']['name']} to {j['legs'][-1]['destination']['name']}"})

    return options
