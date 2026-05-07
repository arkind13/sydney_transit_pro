import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_api_key():
    key = os.getenv("TFNSW_API_KEY")
    if not key:
        try:
            if "TFNSW_API_KEY" in st.secrets:
                key = st.secrets["TFNSW_API_KEY"]
        except:
            pass
    if not key:
        st.error("Missing TFNSW_API_KEY! Please check your .env file.")
    return key