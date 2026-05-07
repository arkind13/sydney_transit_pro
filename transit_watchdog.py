# transit_watchdog.py
import threading
import time
from gps_utils import get_live_gps
from gtfs_realtime import get_trip_delays
from stop_categories import tag_connection_risk

POLL_INTERVAL_SECONDS = 30

def run_watchdog(journey_state, stop_event, gps_mode="manual"):
    while not stop_event.is_set():
        try:
            lat, lng = get_live_gps(mode=gps_mode)
            delays = get_trip_delays()

            risk_results = []
            if journey_state.active_route:
                for leg in journey_state.active_route.get("legs", []):
                    trip_id = leg.get("trip_id", "unknown")
                    delay_secs = delays.get(trip_id, 0)

                    # Now safely calls with 2 args (function accepts default)
                    tagged = tag_connection_risk(leg, delay_secs)
                    risk_results.append(tagged)

            journey_state.watchdog_result = {
                "current_gps": (lat, lng),
                "risk_results": risk_results,
                "timestamp": time.strftime("%H:%M:%S")
            }

        except Exception as e:
            journey_state.watchdog_result = {
                "error": str(e),
                "timestamp": time.strftime("%H:%M:%S")
            }

        stop_event.wait(timeout=POLL_INTERVAL_SECONDS)


def start_watchdog(journey_state, gps_mode="manual"):
    journey_state.watchdog_result = {"timestamp": "Starting first poll..."}
    stop_event = threading.Event()
    thread = threading.Thread(
        target=run_watchdog,
        args=(journey_state, stop_event, gps_mode),
        daemon=True
    )
    thread.start()
    return thread, stop_event