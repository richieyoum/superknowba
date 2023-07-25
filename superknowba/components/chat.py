import streamlit as st
import openai


def chat() -> None:
    # Initialize chat history, if doesn't yet exist
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    # Display chat messages from history
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question"):
        st.session_state["messages"].append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

        # TODO: qachain has response['chat_history'], but can only answer items from db. use general-purpose llm agent to formulate final answer
        if st.session_state["qa_chain"]:
            response = st.session_state["qa_chain"]({"question": prompt})
            for char in response["answer"]:
                full_response += char
                message_placeholder.markdown(full_response + "▌")
        else:
            # TODO: change openai api to langchain chat for consistency
            for response in openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state["messages"]
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
        st.session_state["messages"].append(
            {"role": "assistant", "content": full_response}
        )
