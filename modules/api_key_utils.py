import os
import streamlit as st


def get_google_api_key():
    """Get the Google API key from Streamlit secrets (Cloud and Local) or from .env."""
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = (
            api_key  # Set it in the environment for later use
        )
        return api_key
    except KeyError:
        st.error(
            "API key not found. Please ensure that '.env' exists or provide the key in Streamlit secrets."
        )
        return None
