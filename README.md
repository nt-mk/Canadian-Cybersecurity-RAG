# Canadian Cybersecurity RAG

A Retrieval-Augmented Generation (RAG) project for cybersecurity education.

## Dataset
- 100 cybersecurity documents
- Main source: OWASP Cheat Sheet Series
- 2,599 text chunks indexed
- Document manifest: data/document_manifest.txt

## Technologies
- Python and FastAPI
- ChromaDB vector database
- Sentence Transformers (all-MiniLM-L6-v2)
- Google Gemini API
- Langfuse observability

## RAG Architecture
User Question -> Embedding -> ChromaDB Similarity Search -> Retrieved Context -> Gemini -> Answer

Langfuse records retrieval and RAG execution traces.

## Local Setup
1. Create and activate a Python virtual environment.
2. Install dependencies: pip install -r requirements.txt
3. Create a .env file with GEMINI_API_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, and LANGFUSE_BASE_URL.
4. Index documents: python src/ingestion/ingest.py
5. Start API: uvicorn app.main:app --reload

## API Endpoints
- GET /health
- POST /query

Example POST /query JSON:
{"question": "What is phishing?", "top_k": 3}

## Current Status
Document retrieval and Langfuse retrieval tracing have been tested.
Gemini answer generation and cloud deployment are pending verification.

## Data Attribution
Cybersecurity guidance documents sourced primarily from the OWASP Cheat Sheet Series.
