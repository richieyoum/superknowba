import streamlit as st


def sidebar():
    with st.sidebar:
        st.header("SuperKnowBa 🌌")
        st.subheader("General Settings")
        # set openai key
        st.session_state["openai_api_key"] = st.text_input("OpenAI API Key", placeholder="Paste your OpenAI API Key", type="password")

        st.subheader("Upload your data")
        with st.form("data_form", clear_on_submit=True):
            # TODO: implement and call file-related logic here
            uploaded_file = st.file_uploader(
                "Supported type: pdf, txt, csv, html, docx, md file",
                type=["pdf", "txt", "csv", "html", "docx", "md"],
                accept_multiple_files=True,
                help="Only structured (not scanned) pdfs are supported at this time",
            )
            st.text_input("or, type in webpage url", placeholder="https://")

            # TODO: load in actual db options
            st.session_state["db_option"] = st.selectbox(
                "What DB would you like to upload the data to?",
                ("DB1", "DB2", "DB3"),
            )
            st.form_submit_button("Add and re-index")


        # footer
        st.subheader("Keep in touch!")
        with st.container():
            with st.empty():
                icon, link = st.columns([.05,.95])
                with icon:
                    st.markdown("""
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                        <i class='fa-brands fa-linkedin fa-bounce'/>""",
                        unsafe_allow_html=True
                    )
                link.markdown("[Linkedin](https://www.linkedin.com/in/richieyoum/)")
            with st.empty():
                icon, link = st.columns([.05,.95])
                with icon:
                    st.markdown("""
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                        <i class="fa-brands fa-github fa-bounce"></i>""",
                        unsafe_allow_html=True
                    )
                link.markdown("[Github](https://github.com/richieyoum)")
