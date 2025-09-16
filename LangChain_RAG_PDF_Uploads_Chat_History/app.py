import os
import streamlit as st
from dotenv import load_dotenv

# LangChain community components
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader

# LangChain core utilities
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

# Chains
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# Groq LLM
from langchain_groq import ChatGroq


# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()

# ----------------------------
# Streamlit UI
# ----------------------------
st.title("📄 Conversational RAG with PDF uploads and chat history")
st.write("Upload PDFs and chat with the content interactively.")

# ----------------------------
# API Key Input
# ----------------------------
api_key = st.text_input("Enter your Groq API key", type="password")

# ----------------------------
# If API key available, initialize everything
# ----------------------------
if api_key:
    # HuggingFace embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # LLM (Groq-hosted; pick a supported one)
    llm = ChatGroq(groq_api_key=api_key, model_name="llama-3.1-8b-instant")

    # Manage session
    session_id = st.text_input("Session ID", value="default_session")
    if "store" not in st.session_state:
        st.session_state["store"] = {}

    # Upload PDFs
    uploaded_files = st.file_uploader(
        "Choose PDF file(s)", type="pdf", accept_multiple_files=True
    )

    documents = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            temp_pdf = f"temp_{uploaded_file.name}"
            with open(temp_pdf, "wb") as file:
                file.write(uploaded_file.getvalue())
            loader = PyPDFLoader(temp_pdf)
            docs = loader.load()
            documents.extend(docs)

    # Build vectorstore
    if documents:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
        splits = text_splitter.split_documents(documents)

        vectorstore = Chroma.from_documents(splits, embeddings)
        retriever = vectorstore.as_retriever()

        # Prompts
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question which might reference "
            "context in the chat history, formulate a standalone question that can be "
            "understood without the chat history. Do not answer the question, just "
            "reformulate it if needed and otherwise return it."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}")
            ]
        )

        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        answer_q_system_prompt = (
            "You are an assistant for the question answering task. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you do not know the answer, say that you do not know. "
            "Use three sentences maximum and keep the answer concise.\n\n"
            "Context:\n{context}"
        )
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", answer_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}")
            ]
        )

        qa_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

        # Session history function
        def get_session_history(session_id):
            if session_id not in st.session_state["store"]:
                st.session_state["store"][session_id] = ChatMessageHistory()
            return st.session_state["store"][session_id]

        # Conversational RAG Chain
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )

        # User Input
        user_input = st.text_input("Ask a question:")
        if user_input:
            session_history = get_session_history(session_id)
            response = conversational_rag_chain.invoke(
                {"input": user_input}, config={"session_id": session_id}
            )
            st.subheader("Answer")
            st.write(response["answer"])
            with st.expander("Session History"):
                st.write(session_history)

else:
    st.warning("⚠️ Please enter your Groq API key to start.")
