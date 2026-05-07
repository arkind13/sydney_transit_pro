# stop_categories.py
from enum import Enum
from typing import Dict, Any

class RiskLevel(Enum):
    OPTIMAL = "Optimal"
    AT_RISK = "At Risk"
    CRITICAL = "Critical"

def tag_connection_risk(leg: Dict[str, Any], delay_seconds: int = 0) -> Dict[str, Any]:
    """
    Safe version that accepts 1 or 2 arguments and never compares dict vs int.
    """
    if not isinstance(leg, dict):
        leg = {}

    stop_name = leg.get("stop_name", "Unknown Stop")

    # Guarantee delay_seconds is always an int
    if isinstance(delay_seconds, (int, float)):
        d = int(delay_seconds)
    else:
        d = 0

    if d < 60:
        risk = RiskLevel.OPTIMAL
    elif d < 300:
        risk = RiskLevel.AT_RISK
    else:
        risk = RiskLevel.CRITICAL

    return {
        "stop_name": stop_name,
        "risk_level": risk,
        "delay_seconds": d
    }