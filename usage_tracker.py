# usage_tracker.py
import pandas as pd
from datetime import datetime
import os
import pytz

USAGE_FILE = "api_usage.csv"
SYDNEY_TZ = pytz.timezone("Australia/Sydney")

# Set your manual adjustment here (e.g., 60 calls already made)
MANUAL_ADJUSTMENT = 59

def log_api_call(api_name="google"):
    """Appends a timestamp to the CSV every time an API is called."""
    now = datetime.now(SYDNEY_TZ)
    data = {"timestamp": [now.strftime("%Y-%m-%d %H:%M:%S")], "api": [api_name]}
    df = pd.DataFrame(data)
    
    if not os.path.isfile(USAGE_FILE):
        df.to_csv(USAGE_FILE, index=False)
    else:
        df.to_csv(USAGE_FILE, mode='a', header=False, index=False)

def get_monthly_usage(month, year, api_name="google"):
    """Calculates the number of calls plus the manual adjustment."""
    logged_count = 0
    if os.path.isfile(USAGE_FILE):
        df = pd.read_csv(USAGE_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        filtered = df[
            (df['timestamp'].dt.month == month) & 
            (df['timestamp'].dt.year == year) & 
            (df['api'] == api_name)
        ]
        logged_count = len(filtered)
    
    # Add the 60 calls you've already made
    total_count = logged_count + MANUAL_ADJUSTMENT
    return total_count, logged_count, MANUAL_ADJUSTMENT
