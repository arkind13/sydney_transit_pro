# journey_state.py
from dataclasses import dataclass
from typing import Optional, Dict
import datetime

@dataclass
class JourneyState:
    status: str = "IDLE"
    destination: Optional[str] = None
    active_route: Optional[Dict] = None
    start_time: Optional[datetime.datetime] = None
    # Track the furthest station index reached to auto-green previous stops
    max_stop_index: int = -1 

def initialise_state() -> JourneyState:
    """Returns a fresh JourneyState at IDLE."""
    return JourneyState()

def start_journey(state: JourneyState, origin_gps: tuple, destination: str, active_route: dict) -> JourneyState:
    """Transitions state to ACTIVE and resets tracking indices[cite: 2]."""
    state.status = "ACTIVE"
    state.destination = destination
    state.active_route = active_route
    state.start_time = datetime.datetime.now()
    state.max_stop_index = -1 
    return state

def complete_journey(state: JourneyState) -> JourneyState:
    """Resets the state to IDLE[cite: 2]."""
    state.status = "IDLE"
    state.max_stop_index = -1
    return state