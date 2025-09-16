# Generative AI Projects

A collection of hands-on **Generative AI projects** exploring different LLMs, frameworks, and tools.  
This repository demonstrates practical applications of **OpenAI**, **Ollama**, **LangChain**, **Streamlit**, **Groq** and more.

---

## 📂 Projects

### 1. [LangChain_Chatbot_OpenAI_Ollama](LangChain_Chatbot_OpenAI_Ollama)
A conversational chatbot built with **Streamlit** and **LangChain**, supporting:
- **OpenAI GPT models** (gpt-3.5, gpt-4)
- **Ollama local models** (gemma, llama2, mistral, etc.)

Features:
- Session-based chat history (`Chat-1`, `Chat-2`, …)
- Memory: remembers past interactions in each session
- Configurable **temperature** & **max tokens**
- Hybrid LLM support (local + cloud)

---

### 2. [LangChain_PDF_Groq_Ollama_Embeddings](LangChain_PDF_Groq_Ollama_Embeddings)
A tool to query PDF documents using Retrieval-Augmented Generation (RAG). The app splits PDFs into chunks, embeds them locally using Ollama, stores in FAISS for vector similarity search, and uses Groq-hosted models for generating answers. 
Uses:
- Python, Streamlit  
- LangChain + LangChain-community components  
- Groq API for LLM inference (using a supported model)  
- Ollama for embeddings  
- FAISS for vector search 

Features:
- Splits PDF documents into text chunks using a recursive character splitter.  
- Embeds chunks via an Ollama model.  
- Stores embeddings in a persistent FAISS vector store so embeddings don’t need to be recomputed on each run.  
- Provides a Streamlit UI with a sidebar control to “Click for Document Embedding”, a prominent query input, and displays both the answer and similarity-matched document sections.

---

### 3. [LangChain_RAG_PDF_Uploads_Chat_History](LangChain_RAG_PDF_Uploads_Chat_History)
This project is an **upgraded version** of [LangChain_PDF_Groq_Ollama_Embeddings](../LangChain_PDF_Groq_Ollama_Embeddings).  

Uses:
- [Streamlit](https://streamlit.io/) – Interactive UI  
- [LangChain](https://www.langchain.com/) – RAG orchestration  
- [Groq](https://console.groq.com/) – Fast LLM inference (`llama-3.1-8b-instant`)  
- [HuggingFace Embeddings](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) – Semantic search embeddings  
- [ChromaDB](https://www.trychroma.com/) – Vector database  
- [pypdf](https://pypi.org/project/pypdf/) – PDF text extraction  

Features:
-  **Conversational Memory**: Keeps track of session history using `RunnableWithMessageHistory`.  
-  **Chat Context Awareness**: Reformulates questions based on chat history (`create_history_aware_retriever`).  
-  **Multiple PDF Uploads**: Upload and query multiple PDFs in the same session.  
-  **Chroma Vector Store**: Uses [ChromaDB](https://www.trychroma.com/) instead of FAISS, optimized for conversational use.  
-  **Streamlit UI Enhancements**:
---


## 🚀 Getting Started

Clone the repo:
```bash
git clone https://github.com/vinit-devops/Generative-AI-Projects.git
cd Generative-AI-Projects

