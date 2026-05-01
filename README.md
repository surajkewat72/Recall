# Recall RAG: High-Performance Google Drive Q&A System

Recall RAG is a production-ready Retrieval-Augmented Generation (RAG) platform that enables users to interact with their Google Drive documents through a sleek, custom web interface. Built with **FastAPI**, **ChromaDB**, and **Groq**, it achieves near-instant document synchronization and intelligent, grounded response generation.

![Custom Web UI](https://raw.githubusercontent.com/surajkewat72/Recall/main/app/static/ui_screenshot.png) *(Placeholder for screenshot)*

## 🚀 Key Features

*   **Smart Google Drive Syncing**: 
    *   Sync your entire drive or paste a specific file URL to ingest a single document.
    *   **Incremental Syncing**: Automatically detects updated files via `modifiedTime` and only re-indexes what’s necessary.
    *   Supports PDF, Google Docs, and Text files.
*   **Production-Ready Authentication**: 
    *   Supports **Service Account** authentication for headless cloud deployments (like Hugging Face).
    *   Falls back to OAuth2 for local desktop testing.
*   **Blazing Fast Performance**:
    *   **Asynchronous Pipeline**: Parallelized document parsing, embedding, and indexing using `asyncio`.
    *   **Groq Llama 3.3 Integration**: Sub-second LLM response times using state-of-the-art Llama 3.3 models.
    *   **Intelligent Caching**: LRU caching for embeddings and result-level caching for repeated queries.
*   **Zero-Config Vector Store**: 
    *   Uses **ChromaDB** for local, persistent vector storage. No Docker required!
*   **Premium Web UI**:
    *   Glassmorphism design with a dark-mode aesthetic.
    *   Real-time chat window with source document attribution.
    *   File-level filtering for precise searching.

## 🛠️ Tech Stack

*   **Backend**: FastAPI (Python 3.12+)
*   **LLM**: Groq (Llama-3.3-70b-versatile)
*   **Embeddings**: HuggingFace (`all-MiniLM-L6-v2`)
*   **Database**: ChromaDB (Local Persistent)
*   **Connectors**: Google Drive API v3
*   **Frontend**: Vanilla HTML/CSS/JS (Modern Glassmorphism)

## 📦 Project Structure

```text
Recall/
├── app/
│   ├── api/          # Orchestration layer, endpoints, and caching
│   ├── connectors/   # Google Drive API integration (OAuth & Service Accounts)
│   ├── core/         # Pydantic settings and security
│   ├── embedding/    # Local embedding generation (LRU cached)
│   ├── processing/   # Async document parsing and chunking
│   ├── search/       # ChromaDB vector store logic
│   ├── static/       # Premium Web UI (HTML/CSS/JS)
│   └── main.py       # Application entrypoint
├── chroma_db/        # Persistent vector database storage
├── credentials.json  # Google Cloud credentials (JSON)
├── requirements.txt  # Project dependencies
└── .env              # Environment variables (API Keys)
```

## ⚙️ Setup & Installation

### 1. Prerequisites
*   Python 3.12+
*   A **Groq API Key** (Get one at [console.groq.com](https://console.groq.com))
*   A **Google Cloud Project** with Google Drive API enabled.

### 2. Installation
```bash
# Clone the repo
git clone https://github.com/surajkewat72/Recall.git
cd Recall

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Google Credentials Setup
1.  In Google Cloud Console, create a **Service Account** and download the **JSON Key**.
2.  Rename the downloaded key to `credentials.json` and place it in the project root.
3.  **Share** your Google Drive folder with the Service Account email address.

### 4. Environment Variables
Create a `.env` file in the root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

## 🏃 Running the Project

```bash
uvicorn app.main:app --reload
```

*   **Web UI**: Visit [http://localhost:8000/](http://localhost:8000/)
*   **API Docs**: Visit [http://localhost:8000/docs](http://localhost:8000/docs)

## 🧪 Usage Guide

1.  **Sync**: Paste a Google Drive file link into the sidebar or leave it blank to sync everything shared with the bot.
2.  **Chat**: Ask questions like "What is the refund policy?" or "Summarize the project status."
3.  **Filter**: Use the "Filter by filename" box to limit the AI's knowledge to a specific document.

## 📄 License
MIT License. Created for the AI Platform Engineer Assignment.
