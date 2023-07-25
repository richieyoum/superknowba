import logging
import os
from io import BytesIO
from typing import List
import time
import streamlit as st
from streamlit.components.v1 import html
from streamlit.delta_generator import DeltaGenerator
from superknowba.components.contact import contact
from superknowba.core.document import read_file
from superknowba.core.qa import get_qa_retrieval_chain
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.vectorstores.base import VectorStore
import openai

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if "openai_api_key" in st.session_state:
    openai.api_key = st.session_state["openai_api_key"]
    os.environ["OPENAI_API_KEY"] = st.session_state["openai_api_key"]


def sidebar() -> None:
    with st.sidebar:
        st.header("SuperKnowBa 🌌")
        st.subheader("General Settings")

        #### general settings ####
        # set openai key
        st.session_state["openai_api_key"] = st.text_input(
            "OpenAI API Key",
            placeholder="Paste your OpenAI API Key",
            type="password",
        )
        #### talking with a DB ####
        st.subheader("Talk with your DB")
        with st.form("data_talk_form"):
            selected_db_div = st.empty()
            display_current_db(selected_db_div)
            st.session_state["db_talk_option"] = st.selectbox(
                "Choose the DB to talk to",
                ["ChatGPT"] + st.session_state["database_list"],
                help="Currently, we only support single-DB at a time. Multi-DB support coming soon!",
            )
            talk_option_submit = st.form_submit_button("Apply")

        if talk_option_submit:
            # when user selects an option for db to chat with, update vectordb in use
            if st.session_state["db_talk_option"] != "ChatGPT":
                st.session_state["vectordb"] = get_vectordb(
                    st.session_state["db_talk_option"]
                )
                llm = ChatOpenAI(
                    model=st.session_state["openai_model"],
                    temperature=0.5,
                    streaming=True,
                )
                st.session_state["qa_chain"] = get_qa_retrieval_chain(
                    llm, st.session_state["vectordb"]
                )
            else:
                st.session_state["vectordb"] = None
                st.session_state["qa_chain"] = None
            display_current_db(selected_db_div)

        #### uploading data to DB ####
        st.subheader("Upload your data")

        with st.form("data_upload_form", clear_on_submit=True):
            # files to upload
            st.markdown("### Files")

            # accept single or multiple files
            st.session_state["uploaded_files"] = st.file_uploader(
                "Supported type: pdf",
                type=[
                    "pdf",
                    "txt",
                    "csv",
                    "docx",
                ],  # TODO: Add support for "html", "md"
                accept_multiple_files=True,
                help="Only structured (not scanned) pdfs are supported at this time",
            )

            # also accepts URL for web scraping / YouTube
            # st.text_input("or, type in webpage url", placeholder="https://")

            # db to create / choose
            st.markdown("### Database")

            st.session_state["create_dbname"] = st.text_input(
                "Create a new database and store data",
                placeholder="Name of your new DB",
            )
            st.session_state["db_upload_option"] = st.selectbox(
                "Or, select existing database to save data",
                ["N/A"] + st.session_state["database_list"],
                help="If you don't see your database, try refreshing and check again.",
            )

            data_upload_submit = st.form_submit_button("Add and re-index")

        if data_upload_submit and not st.session_state["uploaded_files"]:
            st.warning("Files missing!")

        if data_upload_submit and st.session_state["uploaded_files"]:
            # user tries to create a DB
            if st.session_state["create_dbname"]:
                # can't do both creation and selection
                if st.session_state["db_upload_option"] != "N/A":
                    st.warning("You can't create and select db at the same time!")
                # can't use existing name for the new DB
                if (
                    st.session_state["create_dbname"]
                    in st.session_state["database_list"]
                ):
                    st.warning(
                        "Database name already exists! Please choose another name."
                    )
                else:
                    # used by save_files_to_db for saving vectorstore
                    st.session_state["db_upload_option"] = st.session_state[
                        "create_dbname"
                    ]
                    save_files_to_db(
                        files=st.session_state["uploaded_files"],
                        db_name=st.session_state["db_upload_option"],
                    )
            # user tries to select a DB
            else:
                if st.session_state["db_upload_option"] != "N/A":
                    save_files_to_db(
                        files=st.session_state["uploaded_files"],
                        db_name=st.session_state["db_upload_option"],
                    )
                # user does neither DB creation or selection
                else:
                    st.warning(
                        "You must create a database or select a database to upload data to"
                    )

            # update database_list states with the new db
            st.session_state["database_list"] = os.listdir("superknowba/vectorstores")

            # clear form states to default
            st.session_state["db_upload_option"] = "N/A"
            st.session_state["uploaded_files"] = None
            st.session_state["create_dbname"] = None

        # footer
        contact()

    # remove default top and bottom padding
    st.markdown(
        """
        <style>
            .css-1544g2n {
            padding: 1.5rem 1rem 1.5rem;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )


def display_current_db(container: DeltaGenerator) -> None:
    current_db = (
        "ChatGPT"
        if "db_talk_option" not in st.session_state
        else st.session_state["db_talk_option"]
    )
    container.write(f"Current DB: **{current_db}**")


def get_vectordb(db_name: str) -> VectorStore:
    db_path = os.path.join("superknowba/vectorstores", db_name)
    return FAISS.load_local(db_path, OpenAIEmbeddings())


def save_files_to_db(files: List[BytesIO], db_name: str) -> None:
    text_splitter = RecursiveCharacterTextSplitter()
    if files:
        embeddings = OpenAIEmbeddings()
        for _file in files:
            file = read_file(_file)
            chunks = text_splitter.split_documents(file.docs)
            db_path = os.path.join("superknowba/vectorstores", db_name)
            try:
                db = FAISS.load_local(db_path, embeddings)
                db.add_documents(chunks)
                db.save_local(db_path)
            except Exception as e:
                logger.error(f"Error loading FAISS index: {e}")
                logger.error("Initializing new db instead")
                db = FAISS.from_documents(documents=chunks, embedding=embeddings)
                db.save_local(db_path)
            finally:
                st.warning(
                    f"Added {len(files)} file(s) to {db_name} successfully. Reloading page..."
                )
                time.sleep(2)
                reload_page()
    else:
        st.warning("No file to upload or file format is incompatible!")


def reload_page() -> None:
    html("<script>parent.window.location.reload()</script>")
