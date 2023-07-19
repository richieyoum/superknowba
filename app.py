import streamlit as st
from dotenv import load_dotenv
import os
import openai
from superknowba.components import chat, sidebar

# load default key, if it exists in .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# set titles
st.set_page_config(page_title="SuperKnowBa", page_icon="🌌", layout="wide")
st.header("SuperKnowBa 🌌")

# list of existing databases
st.session_state["database_list"] = os.listdir("vectorstores/")

# load sidebar component
sidebar()

# if user supplied openai key on sidebar UI, overwrite the default key
if st.session_state["openai_api_key"]:
    openai.api_key = st.session_state["openai_api_key"]

# warn user if openai key not available
if not openai.api_key:
    st.warning(
        "Please enter your OpenAI API key. You can find it here: https://platform.openai.com/account/api-keys."
    )

# TODO: add UI option for selecting different models
# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# load chat component
chat()
