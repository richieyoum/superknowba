import streamlit as st
from superknowba.core.document import read_file
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
            st.session_state["uploaded_files"] = st.file_uploader(
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

            st.session_state["create_dbname"] = st.text_input(
                "Create a new database and store data",
                placeholder="Name of your new DB",
            )
            st.session_state["db_option"] = st.selectbox(
                "Or, select existing database to save data",
                ["N/A"] + st.session_state["database_list"],
            )

            submit = st.form_submit_button("Add and re-index")

        if submit:
            if st.session_state["create_dbname"]:
                # can't do both creation and selection
                if st.session_state["db_option"] != "N/A":
                    st.warning("You can't create and select db at the same time!")
                # can't create a new db with same name
                if (
                    st.session_state["create_dbname"]
                    in st.session_state["database_list"]
                ):
                    st.warning(
                        "Database name already exists! Please choose another name."
                    )
                else:
                    # used by on_upload_submit for saving vectorstore
                    st.session_state["db_option"] = st.session_state["create_dbname"]
                    on_upload_submit()
                    st.warning(
                        f"Created and added files to {st.session_state['db_option']} successfully."
                    )

            if st.session_state["db_option"] == "N/A":
                # can't skip both creation and selection
                if not st.session_state["create_dbname"]:
                    st.warning(
                        "You must create a database or select a database to upload data to"
                    )
                else:
                    on_upload_submit()
                    st.warning(
                        f"Added files to {st.session_state['db_option']} successfully."
                    )

            # update database_list states with the new db
            st.session_state["database_list"] = os.listdir("superknowba/vectorstores")

            # clear form states to default
            st.session_state["db_option"] = "N/A"
            st.session_state["uploaded_files"] = None
            st.session_state["create_dbname"] = None

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


def on_upload_submit():
    text_splitter = RecursiveCharacterTextSplitter()
    if st.session_state["uploaded_files"]:
        embeddings = OpenAIEmbeddings()
        for _file in st.session_state["uploaded_files"]:
            file = read_file(_file)
            chunks = text_splitter.split_documents(file.docs)
            try:
                db = FAISS.load_local(st.session_state["db_option"], embeddings)
                db.add_documents(chunks)
                db.save_local(
                    os.path.join(
                        "superknowba/vectorstores", st.session_state["db_option"]
                    )
                )
            except Exception as e:
                logger.error(f"Error loading FAISS index: {e}")
                logger.error("Initializing new db instead")
                db = FAISS.from_documents(documents=chunks, embedding=embeddings)
                db.save_local(
                    os.path.join(
                        "superknowba/vectorstores", st.session_state["db_option"]
                    )
                )
    else:
        st.warning("No file to upload or file format is incompatible!")
