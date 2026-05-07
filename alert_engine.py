# alert_engine.py
from trip_planner import get_real_journey_options


def evaluate_and_alert(journey):
    """
    Called by app.py every cycle for backward compatibility.
    Returns: journey object unchanged.
    """
    return journey


def check_alternate_routes(journey, current_position):
    """
    Searches for a faster route from the next upcoming stop to the destination.
    Compares against the remaining time on the current active route.

    Returns:
        None if no better route found
        dict: {
            "new_route": { ... leg_bundles ... },
            "savings_minutes": int,
            "description": str,
            "change_point": str
        } if a faster route exists
    """
    if not journey.active_route or not journey.destination:
        return None

    bundles = journey.active_route.get("leg_bundles", [])
    if not bundles:
        return None

    # --- Find the next upcoming stop ---
    next_stop = None
    remaining_minutes = 0
    idx = 0
    found_next = False

    for bundle in bundles:
        for stop in bundle.get("stops", []):
            if not found_next and idx > journey.max_stop_index:
                next_stop = stop
                found_next = True
            if found_next:
                # Count remaining: this bundle's remaining duration + all subsequent bundles
                pass
            idx += 1

    if not next_stop:
        return None  # Everything passed

    # --- Calculate remaining time on CURRENT route ---
    # Flatten all stops with their bundle assignments
    idx = 0
    remaining_minutes = 0
    bundle_started = {}  # Track which bundles we've started counting

    for bundle in bundles:
        b_stops = bundle.get("stops", [])
        for stop in b_stops:
            if idx > journey.max_stop_index:
                # This stop and all subsequent ones are remaining
                # Add the full duration of this bundle (if not already counted)
                bundle_id = id(bundle)
                if bundle_id not in bundle_started:
                    remaining_minutes += bundle.get("duration_min", 0)
                    bundle_started[bundle_id] = True
                break  # Move to next bundle
            idx += 1

    # --- Search for alternate routes from the upcoming stop ---
    alt_options = get_real_journey_options(
        next_stop["name"],
        journey.destination
    )

    if not alt_options:
        return None

    best_alt = alt_options[0]
    alt_minutes = best_alt.get("total_minutes", 999)

    # Guardrail: ignore absurd "savings" (>30 min is a scheduling artifact, not real)
    savings = remaining_minutes - alt_minutes
    if savings < 3 or savings > 30:
        return None

    # Build description
    change_point = next_stop["name"]

    return {
        "new_route": {
            "leg_bundles": best_alt["leg_bundles"],
            "total_minutes": alt_minutes
        },
        "savings_minutes": savings,
        "description": f"🚀 New route found — saves **{savings} minutes**! Change at **{change_point}**.",
        "change_point": change_point
    }


def check_delay_alert(journey, watchdog_data=None):
    """
    Original delay-check logic for missed connection alerts.
    Returns alert string or None.
    """
    if not watchdog_data or "risk_results" not in watchdog_data:
        return None

    risk_results = watchdog_data["risk_results"]

    for leg in risk_results:
        delay = leg.get("delay_seconds", 0)
        stop = leg.get("stop_name", "")

        if "Redfern" in stop and delay > 120:
            return "⚠️ High risk of missing Redfern bus connection!"
        if "Central" in stop and delay > 180:
            return "⚠️ Delay at Central – consider staying on train to Green Square."
        if delay > 300:
            return "🔴 Major delay detected – rerouting recommended."

    return None