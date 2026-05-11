journey_state.py
import datetime
import pytz
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class JourneyState:
    status: str = "IDLE"
    destination: Optional[str] = None
    active_route: Optional[Dict] = None
    start_time: Optional[datetime.datetime] = None
    max_stop_index: int = -1 
    alert_message: Optional[str] = None
    watchdog_result: Optional[Dict] = None

def initialise_state() -> JourneyState:
    return JourneyState()

def start_journey(state: JourneyState, origin_gps: tuple, destination: str, active_route: dict) -> JourneyState:
    syd = pytz.timezone("Australia/Sydney")
    state.status = "ACTIVE"
    state.destination = destination
    state.active_route = active_route
    state.start_time = datetime.datetime.now(syd)
    state.max_stop_index = -1
    state.alert_message = None
    state.watchdog_result = None
    return state

def complete_journey(state: JourneyState) -> JourneyState:
    state.status = "IDLE"
    state.max_stop_index = -1
    state.alert_message = None
    state.watchdog_result = None
    return state
