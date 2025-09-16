import os
import time
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader


# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# ----------------------------
# Prompt template with chat history
# ----------------------------
prompter = ChatPromptTemplate.from_template(
    """
    Answer the question based on provided context only.
    Please provide accurate answer based on the question.
    <context>
    {context}
    </context>
    Input: {input}
    """
)

# ----------------------------
# LLM Creation
# ----------------------------
groq_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(groq_api_key=groq_key, model_name="llama-3.1-8b-instant")

# ----------------------------
# Create vector embedding with session
# ----------------------------

from langchain_community.vectorstores import FAISS
import os

VECTOR_STORE_PATH = "faiss_index"

def create_vector_embeddings():
    if "vector_store" not in st.session_state:
        if os.path.exists(VECTOR_STORE_PATH):
            st.session_state.vector_store = FAISS.load_local(
                VECTOR_STORE_PATH,
                OllamaEmbeddings(model="embeddinggemma:latest"),
                allow_dangerous_deserialization=True  # required by langchain for pickle-based metadata
            )
            st.session_state.embeddings = OllamaEmbeddings(model="embeddinggemma:latest")
            st.session_state.loader = PyPDFDirectoryLoader("./context-pdf")
            st.session_state.docs = st.session_state.loader.load()
            st.session_state.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=100
            )
            st.session_state.final_doc = st.session_state.text_splitter.split_documents(st.session_state.docs)
        else:
            # ✅ Create FAISS index and save it
            st.session_state.embeddings = OllamaEmbeddings(model="embeddinggemma:latest")
            st.session_state.loader = PyPDFDirectoryLoader("./context-pdf")
            st.session_state.docs = st.session_state.loader.load()
            st.session_state.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=100
            )
            st.session_state.final_doc = st.session_state.text_splitter.split_documents(st.session_state.docs)
            st.session_state.vector_store = FAISS.from_documents(
                st.session_state.final_doc,
                st.session_state.embeddings
            )
            st.session_state.vector_store.save_local(VECTOR_STORE_PATH)

# ----------------------------
# User Input Button
# ----------------------------
st.title("PDF Q&A with Groq + Ollama Embeddings")

st.markdown("**Enter your query from PDF document after PDF document embedding**")
user_prompt = st.text_input("", key="query_input")

with st.sidebar:
    st.subheader("Vector DB Setup")
    if st.button("First Click here Document Embedding"):
        create_vector_embeddings()
        st.success("Database is Ready !!!")

# ----------------------------
# Build document and retrieval chain
# ----------------------------

if user_prompt:
    document_chain = create_stuff_documents_chain(llm, prompter)
    retriever = st.session_state.vector_store.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    response = retrieval_chain.invoke({"input": user_prompt})
    st.write(response)
    with st.expander("Document Similarity Search "):
        for i, doc in enumerate(st.session_state.final_doc):
            st.write(doc.page_content)