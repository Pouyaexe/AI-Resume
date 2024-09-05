import os
import streamlit as st
from dotenv import load_dotenv

def get_google_api_key():
    """Get the Google API key from Streamlit secrets (Cloud and Local) or from .env."""
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        os.environ["GOOGLE_API_KEY"] = api_key  # Set it in the environment for later use
        return api_key
    except KeyError:
        # Fallback to environment variable in local development
        load_dotenv()  # Load the .env file if it exists
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            return api_key
        else:
            st.error("API key not found. Please ensure that '.env' exists or provide the key in Streamlit secrets.")
            return None
