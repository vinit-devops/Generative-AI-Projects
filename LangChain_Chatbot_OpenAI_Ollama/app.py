import os
import uuid
import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# ----------------------------
# Prompt template with chat history
# ----------------------------
prompter = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer clearly and concisely."),
    MessagesPlaceholder("chat_history"),
    ("user", "{input}")
])

# ----------------------------
# LLM selection helper
# ----------------------------
def get_llm(llm_model, api_key, temperature, max_tokens):
    if llm_model.startswith("gpt-"):
        return ChatOpenAI(
            model=llm_model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )
    else:
        return Ollama(
            model=llm_model,
            temperature=temperature
        )

# ----------------------------
# Session history manager
# ----------------------------
def get_session_history(session_id: str) -> ChatMessageHistory:
    if "histories" not in st.session_state:
        st.session_state["histories"] = {}
    if session_id not in st.session_state["histories"]:
        st.session_state["histories"][session_id] = ChatMessageHistory()
    return st.session_state["histories"][session_id]

# ----------------------------
# Build chain with history
# ----------------------------
def get_chain(llm_model, api_key, temperature, max_tokens):
    llm = get_llm(llm_model, api_key, temperature, max_tokens)
    output = StrOutputParser()
    chain = prompter | llm | output

    return RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history"
        # ✅ no output_messages_key (avoids KeyError)
    )

# ----------------------------
# Response provider
# ----------------------------
def response_provider(user_input, llm_model, api_key, temperature, max_tokens, session_id):
    chain = get_chain(llm_model, api_key, temperature, max_tokens)
    response = chain.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}},
    )
    history = get_session_history(session_id)
    return response, history

# ----------------------------
# Streamlit UI
# ----------------------------
st.title("LangChain Chatbot with OpenAI GPT & Ollama Support")

# Init sessions
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = "Chat-1"
    st.session_state.current_session = new_id
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1

# Sidebar
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
llm_model = st.sidebar.selectbox("LLM Model", ["gpt-3.5-turbo", "gpt-4", "gemma:2b"])
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.5)
max_tokens = st.sidebar.slider("Max Tokens (for GPT only)", 50, 1024, 256)

# Session chooser
session_options = list(st.session_state.sessions.values())
current_name = st.session_state.sessions[st.session_state.current_session]
chosen_name = st.sidebar.selectbox("Choose Session", session_options, index=session_options.index(current_name))

# Map chosen name -> session_id
for sid, name in st.session_state.sessions.items():
    if name == chosen_name:
        st.session_state.current_session = sid

# New chat
if st.sidebar.button("Start New Chat"):
    st.session_state.chat_counter += 1
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = f"Chat-{st.session_state.chat_counter}"
    st.session_state.current_session = new_id

st.write(f"### Current Session: `{st.session_state.sessions[st.session_state.current_session]}`")

# Chat input
st.write("## Chat Window")
user_input = st.text_input("You:")

if user_input:
    try:
        response, history = response_provider(
            user_input,
            llm_model,
            api_key,
            temperature,
            max_tokens,
            st.session_state.current_session
        )

        # Only show last assistant answer
        st.markdown(f"**Assistant:** {response}")

    except Exception as e:
        st.error(f"Error: {str(e)}")