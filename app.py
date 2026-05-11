import streamlit as st
import time
import os
from datetime import datetime
from geopy.distance import geodesic

from search_history import (
    add_search, get_recent_searches, get_favourites,
    toggle_favourite, is_favourite,
)

from journey_state import initialise_state, start_journey, complete_journey
from trip_planner import get_real_journey_options
from gps_utils import get_live_gps
from stop_finder import ping_api
from geocoder import get_coordinates, ping_google, get_last_geocode_source
from alert_engine import evaluate_and_alert

# --- TIMEZONE CONFIG ---
os.environ['TZ'] = 'Australia/Sydney'
try:
    time.tzset()
except AttributeError:
    pass

st.set_page_config(page_title="Sydney Transit Pro", page_icon="🚆", layout="wide")

if "journey" not in st.session_state:
    st.session_state.journey = initialise_state()

# ====================== SIDEBAR ======================
with st.sidebar:
    # ── Live Sydney Clock ──
    now_syd = datetime.now()
    st.markdown(f"🕐 **{now_syd.strftime('%H:%M  %d-%b-%Y')}**")
    st.divider()

    st.header("🛠️ Dev Simulation")
    test_mode = st.toggle("Manual GPS Simulation", value=False)

    presets = {
        "🏠 Mount Druitt":       (-33.7690, 150.8192),
        "🏠 Rooty Hill":         (-33.7722, 150.8446),
        "🏠 Doonside":           (-33.7652, 150.8700),
        "🏠 Blacktown":          (-33.7680, 150.9075),
        "🏠 Seven Hills":        (-33.7753, 150.9370),
        "🏠 Toongabbie":         (-33.7876, 150.9522),
        "🏠 Pendle Hill":        (-33.8012, 150.9597),
        "🏠 Wentworthville":     (-33.8104, 150.9753),
        "🏠 Westmead":           (-33.8170, 150.9880),
        "🏠 Parramatta":         (-33.8175, 151.0053),
        "🏠 Harris Park":        (-33.8220, 151.0080),
        "🏠 Granville":          (-33.8323, 151.0131),
        "🏠 Clyde":              (-33.8377, 151.0172),
        "🏠 Auburn":             (-33.8495, 151.0420),
        "🏠 Lidcombe":           (-33.8641, 151.0449),
        "🏠 Homebush":           (-33.8653, 151.0826),
        "🏠 Strathfield":        (-33.8712, 151.0950),
        "🏠 Burwood":            (-33.8770, 151.1054),
        "🏠 Redfern":            (-33.8923, 151.1988),
        "🏁 Central":            (-33.8828, 151.2067),
    }

    selected_preset = st.selectbox(
        "Current Simulated Location:",
        options=list(presets.keys())
    )
    sim_lat, sim_lng = presets[selected_preset]

    st.divider()

    # ── TfNSW API status ──
    api_status = ping_api()
    if api_status["success"]:
        st.success("🔵 TfNSW API: Connected")
    else:
        st.error("🔴 TfNSW API: Connection Failed")

    # ── Google API status ──
    google_status = ping_google()
    if google_status["success"]:
        st.success("🟢 Google Geo: Connected")
    else:
        st.warning(f"🟡 Google Geo: {google_status['message']}")

    # ── Last geocode source (dual: origin + destination) ──
    source_labels = {
        "station_dictionary": "📚 Station Lookup",
        "google_api": "🌐 Google API",
        "nominatim_fallback": "⚠️ Nominatim",
        "empty_query": "—",
        "unknown": "—",
    }
    src_o = st.session_state.get("last_origin_source", "—")
    src_d = st.session_state.get("last_dest_source", "—")
    st.caption(
        f"📍 Origin: {source_labels.get(src_o, src_o)}\n\n"
        f"🎯 Destination: {source_labels.get(src_d, src_d)}"
    )

# ====================== PLANNING PHASE (IDLE) ======================
if st.session_state.journey.status == "IDLE":
    st.title("Sydney Transit Pro")
    st.caption("Live Orchestrator • Phase 2: Live Tracking")

    # ── Search History Dropdown ──
    recent = get_recent_searches()
    if recent:
        history_labels = [
            f"{s['origin']} → {s['destination']}"
            for s in recent
        ]
        history_labels.insert(0, "— Recent searches —")

        selected_history = st.selectbox(
            "📋 Recent Searches",
            options=history_labels,
            index=0,
            label_visibility="collapsed",
        )

        if selected_history != "— Recent searches —":
            idx = history_labels.index(selected_history) - 1
            chosen = recent[idx]
            st.session_state.prefill_origin = chosen["origin"]
            st.session_state.prefill_destination = chosen["destination"]
        else:
            st.session_state.prefill_origin = ""
            st.session_state.prefill_destination = ""

    # ── Origin / Destination Inputs ──
    col1, col2 = st.columns(2)
    with col1:
        origin_raw = st.text_input(
            "Origin",
            value=st.session_state.get("prefill_origin", "Mount Druitt Train Station"),
        )
    with col2:
        destination_raw = st.text_input(
            "Destination",
            value=st.session_state.get("prefill_destination", "Alexandria"),
        )

    # ── Search button ──
    if st.button("🔎 Find Best Options", type="primary"):
        search_origin = origin_raw
        if "station" not in origin_raw.lower():
            search_origin = f"{origin_raw} Station, Sydney"

        search_destination = destination_raw

        lat_o, lng_o, addr_o = get_coordinates(search_origin)
        source_o = get_last_geocode_source()

        lat_d, lng_d, addr_d = get_coordinates(search_destination)
        source_d = get_last_geocode_source()

        st.session_state.last_origin_source = source_o
        st.session_state.last_dest_source = source_d

        from station_lookup import get_station_name as _get_stn
        from geocoder import clean_address

        name_o = _get_stn(search_origin) or search_origin
        name_d = clean_address(search_destination)

        if lat_o is not None and lat_d is not None:
            options = get_real_journey_options(name_o, name_d)
            if options:
                add_search(origin_raw.strip(), destination_raw.strip())
                st.session_state.journey_options = options
                st.session_state.search_origin = name_o
                st.session_state.search_destination = name_d
                st.session_state.origin_coords = (lat_o, lng_o)
            else:
                st.warning("No routes found. Please check stop names.")
        else:
            if lat_o is None:
                st.error(
                    f"❌ Could not locate origin: '{origin_raw}'. "
                    f"Try a station name like 'Mount Druitt' or a full address."
                )
            if lat_d is None:
                st.error(
                    f"❌ Could not locate destination: '{destination_raw}'. "
                    f"Try removing unit numbers, e.g. '37 O'Riordan St, Alexandria NSW 2015'."
                )

    # ── Results ──
    if "journey_options" in st.session_state:
        st.subheader(f"Results from {st.session_state.search_origin}")

        o = st.session_state.get("search_origin", "")
        d = st.session_state.get("search_destination", "")
        fav = is_favourite(o, d)
        fav_label = "⭐ Saved" if fav else "☆ Save"

        if st.button(fav_label, key="fav_current"):
            toggle_favourite(o, d)
            st.rerun()

        for i, opt in enumerate(st.session_state.journey_options):
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([4.5, 1, 1.2, 1.8])
                c1.markdown(
                    f"**{opt['route_description']}**\n"
                    f"🕒 {opt['depart']} → {opt['arrive']}"
                )
                c2.markdown(f"{opt['changes']} changes")
                c3.markdown(f"⏱️ {opt['duration']}")

                if c4.button("Start Journey", key=f"start_{i}"):
                    start_pos = (
                        st.session_state.origin_coords
                        if "origin_coords" in st.session_state
                        else (sim_lat, sim_lng)
                    )
                    st.session_state.journey = start_journey(
                        st.session_state.journey,
                        origin_gps=start_pos,
                        destination=st.session_state.search_destination,
                        active_route={
                            "leg_bundles": opt["leg_bundles"],
                            "total_minutes": opt["total_minutes"],
                        },
                    )
                    st.rerun()

    # ── Favourites ──
    favs = get_favourites()
    if favs:
        with st.expander("⭐ Saved Favourites", expanded=False):
            for fav in favs:
                fc1, fc2 = st.columns([8, 2])
                fc1.markdown(f"**{fav['origin']}** → **{fav['destination']}**")
                if fc2.button("❌", key=f"unfav_{fav['origin']}_{fav['destination']}"):
                    toggle_favourite(fav["origin"], fav["destination"])
                    st.rerun()

# ====================== LIVE JOURNEY PHASE (ACTIVE) ======================
elif st.session_state.journey.status in ["ACTIVE", "ALERTED"]:
    st.title(f"🚆 Tracking to {st.session_state.journey.destination}")

    if test_mode:
        current_pos = (sim_lat, sim_lng)
        st.info(f"🛰️ Simulating Location: **{selected_preset}**")
    else:
        gps_lat, gps_lng = get_live_gps(mode="browser")
        current_pos = (gps_lat, gps_lng)

    if "last_alt_check" not in st.session_state:
        st.session_state.last_alt_check = datetime.now()

    if "pause_alerts" not in st.session_state:
        st.session_state.pause_alerts = False

    time_since_check = (datetime.now() - st.session_state.last_alt_check).total_seconds()

    col_track, col_check, col_pause = st.columns([2.5, 1, 1])
    with col_check:
        manual_check = st.button("🔍 Check Now", use_container_width=True)
    with col_pause:
        if st.session_state.pause_alerts:
            if st.button("▶️ Resume Alerts", use_container_width=True, type="primary"):
                st.session_state.pause_alerts = False
                st.rerun()
        else:
            if st.button("⏸️ Pause Alerts", use_container_width=True):
                st.session_state.pause_alerts = True
                st.rerun()

    if not st.session_state.pause_alerts:
        if time_since_check >= 90 or manual_check:
            from alert_engine import check_alternate_routes
            alt_result = check_alternate_routes(st.session_state.journey, current_pos)
            st.session_state.last_alt_check = datetime.now()

            if alt_result:
                st.session_state.last_alt_result = alt_result
                st.session_state.journey.status = "ALERTED"
                st.session_state.journey.alert_message = alt_result["description"]
                st.session_state.journey.watchdog_result = {
                    "new_route": alt_result["new_route"]
                }
                st.rerun()
            else:
                st.session_state.last_alt_result = None
                st.session_state.journey.alert_message = None
                st.session_state.journey.watchdog_result = {}
                st.rerun()

    if st.session_state.pause_alerts:
        st.info("🔕 Auto-check paused — tap **▶️ Resume Alerts** to re-enable.")
    else:
        if "last_alt_result" in st.session_state:
            result = st.session_state.last_alt_result
            if result is None:
                st.success("✅ No faster route available — you're on the best option.")
            else:
                current_time = st.session_state.journey.active_route.get("total_minutes", "?")
                new_time = result["new_route"]["total_minutes"]
                savings = result["savings_minutes"]

                st.warning(f"🚀 **Faster route found!** Saves **{savings} minutes**.")
                st.markdown(
                    f"| | Current Route | New Route |\n"
                    f"|---|---|---|\n"
                    f"| ⏱️ Travel Time | {current_time} min | {new_time} min |\n"
                    f"| 🔄 Change Point | — | **{result['change_point']}** |\n"
                    f"| 💡 Saves | — | **{savings} min** |"
                )
        elif (st.session_state.journey.status == "ALERTED"
              and st.session_state.journey.alert_message):
            st.warning(st.session_state.journey.alert_message)

    evaluate_and_alert(st.session_state.journey)

    if (st.session_state.journey.status == "ALERTED"
            and st.session_state.journey.watchdog_result
            and "new_route" in st.session_state.journey.watchdog_result):

        col_acc, col_rej = st.columns(2)

        if col_acc.button("✅ Accept New Route"):
            st.session_state.journey.active_route = (
                st.session_state.journey.watchdog_result["new_route"]
            )
            st.session_state.journey.status = "ACTIVE"
            st.session_state.journey.alert_message = None
            st.session_state.journey.max_stop_index = -1
            st.session_state.last_alt_result = None
            st.success("Journey Updated!")
            st.rerun()

        if col_rej.button("❌ Dismiss"):
            st.session_state.journey.status = "ACTIVE"
            st.session_state.last_alt_result = None
            st.rerun()

    if st.button("← Back to Search"):
        st.session_state.journey = initialise_state()
        st.rerun()

    # Progress Tracking
    bundles = st.session_state.journey.active_route.get("leg_bundles", [])
    st.subheader("🛤️ Stations & Progress")

    global_stop_idx = 0
    for b_idx, bundle in enumerate(bundles):
        icon = "🚆" if bundle["mode"] == "TRAIN" else "🚌" if bundle["mode"] == "BUS" else "🚶"

        with st.expander(
            f"{icon} {bundle['action']}: {bundle['origin']} ⮕ {bundle['destination']}",
            expanded=True
        ):
            if bundle["stops"]:
                for stop in bundle["stops"]:
                    stop_pos = (stop["lat"], stop["lng"])
                    dist = geodesic(current_pos, stop_pos).meters

                    if dist < 500:
                        if global_stop_idx > st.session_state.journey.max_stop_index:
                            st.session_state.journey.max_stop_index = global_stop_idx

                    is_passed = global_stop_idx <= st.session_state.journey.max_stop_index
                    if is_passed:
                        st.markdown(f":green[✅ {stop['name']} (Passed)]")
                    else:
                        st.markdown(f"◦ {stop['name']} ({stop['planned_arrival']})")

                    global_stop_idx += 1
            else:
                st.markdown(f"_{bundle['action']} for {bundle['duration_min']} mins_")

    st.divider()

    if "last_alt_check" in st.session_state and not st.session_state.pause_alerts:
        next_check = max(0, 90 - time_since_check)
        st.caption(f"⏱️ Next auto-check in {int(next_check)}s | Auto-checks every 90s")

    if st.button("🛑 End Journey", use_container_width=True, type="primary"):
        st.session_state.journey = complete_journey(st.session_state.journey)
        st.rerun()

    time.sleep(15)
    st.rerun()
