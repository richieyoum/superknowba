import streamlit as st


def check_key_notnull(key: str) -> bool:
    """Check if the key exists in the session state, as well as its value not being null"""
    return key in st.session_state and st.session_state[key]
