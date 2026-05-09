# config.py
import os
import streamlit as st


def get_api_key():
    """
    Load the TfNSW API key.
    Checks in order:
      1. Streamlit secrets (covers .streamlit/secrets.toml + Cloud dashboard)
      2. Environment variable (fallback if running outside Streamlit)
    """
    # 1. Streamlit secrets (preferred)
    key = st.secrets.get("TNSW_API_KEY", "")

    # 2. Environment variable fallback
    if not key:
        key = os.getenv("TFNSW_API_KEY", "")

    if not key:
        st.error("Missing TNSW_API_KEY! Add it to .streamlit/secrets.toml or environment.")

    return key
