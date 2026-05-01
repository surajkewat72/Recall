# RAG with Google Drive

This is a production-ready Python FastAPI project for a Retrieval-Augmented Generation (RAG) system that connects with Google Drive.

## Project Structure

```
rag-gdrive/
├── app/
│   ├── api/          # FastAPI routers and dependencies
│   ├── connectors/   # External system integrations (Google Drive)
│   ├── core/         # Core application settings and configs
│   ├── embedding/    # Vector embedding logic
│   ├── processing/   # Document chunking and parsing
│   ├── search/       # Vector database integration
│   ├── main.py       # FastAPI application entrypoint
├── .env.example      # Example environment variables
├── requirements.txt  # Project dependencies
```

## Setup

1. Clone the repository and navigate to the project directory:
   ```bash
   cd rag-gdrive
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file and add your credentials.

4. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Access the API documentation:
   Open your browser and navigate to `http://localhost:8000/docs`.
