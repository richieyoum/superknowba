import streamlit as st


def sidebar():
    with st.sidebar:
        st.header("SuperKnowBa 🌌")
        st.subheader("General Settings")

        #### general settings ####
        # set openai key
        st.session_state["openai_api_key"] = st.text_input(
            "OpenAI API Key", placeholder="Paste your OpenAI API Key", type="password"
        )

        #### uploading data to DB ####
        st.subheader("Upload your data")

        with st.form("data_form", clear_on_submit=True):
            # files to upload
            st.markdown("### Files")

            # accept single or multiple files
            uploaded_file = st.file_uploader(
                "Supported type: pdf",
                type=[
                    "pdf"
                ],  # TODO: Add support for "txt", "csv", "html", "docx", "md"
                accept_multiple_files=True,
                help="Only structured (not scanned) pdfs are supported at this time",
            )

            # also accepts URL for web scraping / YouTube
            st.text_input("or, type in webpage url", placeholder="https://")

            # db to create / choose
            st.markdown("### Database")

            st.text_input(
                "Create a new database and store data",
                placeholder="Name of your new DB",
            )
            st.session_state["db_option"] = st.selectbox(
                "Or, select existing database to save data",
                st.session_state["database_list"],
            )

            st.form_submit_button("Add and re-index")

        # footer
        st.subheader("Keep in touch!")
        with st.container():
            with st.empty():
                icon, link = st.columns([0.05, 0.95])
                with icon:
                    st.markdown(
                        """
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                        <i class='fa-brands fa-linkedin fa-bounce'/>""",
                        unsafe_allow_html=True,
                    )
                link.markdown("[Linkedin](https://www.linkedin.com/in/richieyoum/)")
            with st.empty():
                icon, link = st.columns([0.05, 0.95])
                with icon:
                    st.markdown(
                        """
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
                        <i class="fa-brands fa-github fa-bounce"></i>""",
                        unsafe_allow_html=True,
                    )
                link.markdown("[Github](https://github.com/richieyoum)")
