import streamlit as st
from dotenv import load_dotenv
import os
import openai
from components.sidebar import sidebar

# load default key, if it exists in .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="SuperKnowBa", page_icon="🌌", layout="wide")
st.header("SuperKnowBa 🌌")

# load sidebar component
sidebar()

# if user supplied openai key on UI, overwrite the default key
if st.session_state["openai_api_key"]:
    openai.api_key = st.session_state["openai_api_key"]

if not openai.api_key:
    st.warning(
        "Please enter your OpenAI API key. You can find it here: https://platform.openai.com/account/api-keys."
    )

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

    for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        ):
        full_response += response.choices[0].delta.get("content", "")
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
