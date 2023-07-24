import streamlit as st
from superknowba.core.document import read_file
from superknowba.core.qa import get_qa_retrieval_chain
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.vectorstores.base import VectorStore
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def sidebar() -> None:
    with st.sidebar:
        st.header("SuperKnowBa 🌌")
        st.subheader("General Settings")

        #### general settings ####
        # set openai key
        st.session_state["openai_api_key"] = st.text_input(
            "OpenAI API Key", placeholder="Paste your OpenAI API Key", type="password"
        )

        #### talking with a DB ####
        st.subheader("Talk with your DB")
        with st.form("data_talk_form"):
            st.session_state["db_talk_option"] = st.selectbox(
                "Choose the DB to talk to",
                st.session_state["database_list"],
                help="Currently, we only support single-DB at a time. Multi-DB support coming soon!",
            )
            talk_option_submit = st.form_submit_button("Apply")

        if talk_option_submit:
            # when user selects an option for db to chat with, update vectordb in use
            if st.session_state["db_talk_option"]:
                st.session_state["vectordb"] = get_db_from_chat_selection()
                llm = ChatOpenAI(
                    model=st.session_state["openai_model"],
                    temperature=0.5,
                    streaming=True,
                )
                st.session_state["qa_chain"] = get_qa_retrieval_chain(
                    llm, st.session_state["vectordb"]
                )
            else:
                st.warning(
                    "Please create a database first, then select a database to chat with. Otherwise, you're simply chatting with default ChatGPT"
                )

        #### uploading data to DB ####
        st.subheader("Upload your data")

        with st.form("data_upload_form", clear_on_submit=True):
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
                    save_files_to_db()
                    st.warning(
                        f"Created and added {len(st.session_state['uploaded_files'])} file(s) to {st.session_state['db_upload_option']} successfully."
                    )
            # user tries to select a DB
            else:
                if st.session_state["db_upload_option"] != "N/A":
                    save_files_to_db()
                    st.warning(
                        f"Added {len(st.session_state['uploaded_files'])} file(s) to {st.session_state['db_upload_option']} successfully."
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


def get_db_from_chat_selection() -> VectorStore:
    db_path = os.path.join(
        "superknowba/vectorstores", st.session_state["db_talk_option"]
    )
    return FAISS.load_local(db_path, OpenAIEmbeddings())


def save_files_to_db() -> None:
    text_splitter = RecursiveCharacterTextSplitter()
    if st.session_state["uploaded_files"]:
        embeddings = OpenAIEmbeddings()
        for _file in st.session_state["uploaded_files"]:
            file = read_file(_file)
            chunks = text_splitter.split_documents(file.docs)
            db_path = os.path.join(
                "superknowba/vectorstores", st.session_state["db_upload_option"]
            )
            try:
                db = FAISS.load_local(db_path, embeddings)
                db.add_documents(chunks)
                db.save_local(db_path)
            except Exception as e:
                logger.error(f"Error loading FAISS index: {e}")
                logger.error("Initializing new db instead")
                db = FAISS.from_documents(documents=chunks, embedding=embeddings)
                db.save_local(db_path)
    else:
        st.warning("No file to upload or file format is incompatible!")
