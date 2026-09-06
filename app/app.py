import sys
from pathlib import Path

import streamlit as st


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# =========================================================
# BACKEND IMPORTS
# =========================================================

from functions import (
    ask_question,
    extract_structured_info,
    structured_info_to_dataframe,
    get_retrieved_chunks,
    get_knowledge_base_info
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="RAG Document Assistant",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        color: #888888;
        margin-bottom: 25px;
    }

    .source-card {
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #444444;
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">📚 RAG Document Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Ask questions and extract structured information from
    your document knowledge base using Retrieval-Augmented Generation.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Options")


mode = st.sidebar.radio(
    "Choose a mode:",
    [
        "💬 Ask a Question",
        "📊 Extract Information"
    ]
)


# =========================================================
# KNOWLEDGE BASE
# =========================================================

st.sidebar.divider()

st.sidebar.subheader("📚 Knowledge Base")


try:

    kb_info = get_knowledge_base_info()

    st.sidebar.write(
        f"**Chunks:** {kb_info['total_chunks']}"
    )

    if kb_info["documents"]:

        st.sidebar.write("**Documents:**")

        for document in kb_info["documents"]:

            st.sidebar.caption(
                f"📄 {document}"
            )

    else:

        st.sidebar.caption(
            "No document information available."
        )


except Exception:

    st.sidebar.caption(
        "Knowledge base information unavailable."
    )


# =========================================================
# MODEL INFORMATION
# =========================================================

st.sidebar.divider()

st.sidebar.subheader("🤖 AI Model")

st.sidebar.write(
    "Llama 3.1 8B Instruct"
)

st.sidebar.subheader("🔎 Embeddings")

st.sidebar.write(
    "all-MiniLM-L6-v2"
)


# =========================================================
# CLEAR CHAT
# =========================================================

if mode == "💬 Ask a Question":

    st.sidebar.divider()

    if st.sidebar.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# =========================================================
# ASK QUESTION MODE
# =========================================================

if mode == "💬 Ask a Question":

    st.header("💬 Ask a Question")

    st.write(
        "Ask questions about information contained "
        "in your document knowledge base."
    )


    # -----------------------------------------------------
    # DISPLAY CHAT HISTORY
    # -----------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

            # Display sources for assistant messages
            if (
                message["role"] == "assistant"
                and message.get("sources")
            ):

                with st.expander(
                    "📄 View Sources"
                ):

                    for source in message["sources"]:

                        st.markdown(
                            f"""
                            **Source:** {source["document"]}  
                            **Page:** {source["page"]}
                            """
                        )

                        st.caption(
                            source["content"]
                        )

                        st.divider()


    # -----------------------------------------------------
    # CHAT INPUT
    # -----------------------------------------------------

    question = st.chat_input(
        "Ask something about your documents..."
    )


    if question:

        # -------------------------------------------------
        # DISPLAY USER QUESTION
        # -------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message("user"):

            st.markdown(question)


        # -------------------------------------------------
        # GENERATE ANSWER
        # -------------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "Searching documents and generating answer..."
            ):

                try:

                    answer = ask_question(
                        question
                    )


                    # -------------------------------------
                    # RETRIEVE SOURCE CHUNKS
                    # -------------------------------------

                    relevant_chunks = (
                        get_retrieved_chunks(
                            question
                        )
                    )


                    sources = []


                    for chunk in relevant_chunks:

                        metadata = (
                            chunk.metadata or {}
                        )


                        source_path = metadata.get(
                            "source",
                            "Unknown document"
                        )


                        document_name = (
                            Path(source_path).name
                            if source_path != "Unknown document"
                            else "Unknown document"
                        )


                        page = metadata.get(
                            "page",
                            "Unknown"
                        )


                        # Convert zero-based PDF page
                        # number to human-readable page
                        if isinstance(page, int):

                            page = page + 1


                        sources.append(
                            {
                                "document": document_name,
                                "page": page,
                                "content": chunk.page_content
                            }
                        )


                    # -------------------------------------
                    # DISPLAY ANSWER
                    # -------------------------------------

                    st.markdown(answer)


                    # -------------------------------------
                    # DISPLAY SOURCES
                    # -------------------------------------

                    if sources:

                        with st.expander(
                            f"📄 Sources ({len(sources)})"
                        ):

                            for source in sources:

                                st.markdown(
                                    f"""
                                    **📄 Document:** {source["document"]}

                                    **📑 Page:** {source["page"]}
                                    """
                                )

                                st.caption(
                                    source["content"]
                                )

                                st.divider()


                    else:

                        st.info(
                            "No source information was available."
                        )


                    # -------------------------------------
                    # SAVE ASSISTANT MESSAGE
                    # -------------------------------------

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        }
                    )


                except Exception as e:

                    error_message = (
                        f"An error occurred: {str(e)}"
                    )

                    st.error(
                        error_message
                    )


# =========================================================
# STRUCTURED EXTRACTION MODE
# =========================================================

else:

    st.header("📊 Extract Document Information")

    st.write(
        "Extract predefined information from your "
        "documents and display the result in a structured table."
    )


    extraction_question = st.text_area(
        "Extraction request",

        value=(
            "Extract the key information about Apple "
            "from the provided document."
        ),

        height=120
    )


    extract_button = st.button(
        "📊 Extract Information",
        use_container_width=True
    )


    if extract_button:

        if not extraction_question.strip():

            st.warning(
                "Please enter an extraction request."
            )


        else:

            with st.spinner(
                "Retrieving information and extracting fields..."
            ):

                try:

                    result = extract_structured_info(
                        extraction_question
                    )


                    df = structured_info_to_dataframe(
                        result
                    )


                    st.subheader(
                        "📋 Extracted Information"
                    )


                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )


                    # -------------------------------------
                    # DOWNLOAD CSV
                    # -------------------------------------

                    csv_data = df.to_csv(
                        index=False
                    )


                    st.download_button(
                        label="⬇️ Download CSV",

                        data=csv_data,

                        file_name=(
                            "extracted_information.csv"
                        ),

                        mime="text/csv"
                    )


                except Exception as e:

                    st.error(
                        f"An error occurred: {str(e)}"
                    )