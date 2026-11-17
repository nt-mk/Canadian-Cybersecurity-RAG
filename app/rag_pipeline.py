import os
from app.ollama_client import generate_answer as ollama_generate_answer
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from app.gemini_client import generate_answer
from langfuse import observe

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "chroma_db"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None

@observe(name="document_retrieval")
def retrieve_documents(question: str, top_k: int = 3):
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=str(DB_PATH))
    collection = client.get_collection("cybersecurity_docs")

    embedding = _model.encode(
        [question], normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    return [
        {
            "text": document,
            "source": metadata["source"],
            "distance": distance
        }
        for document, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )
    ]

@observe(name="rag_query")
def answer_question(question: str, top_k: int = 3):
    documents = retrieve_documents(question, top_k)

    context = "\n\n".join(
        f"Source: {doc['source']}\n{doc['text']}"
        for doc in documents
    )

    answer = (ollama_generate_answer(question, context) if os.getenv("LLM_PROVIDER", "ollama").lower() == "ollama" else generate_answer(question, context))

    return {
        "question": question,
        "answer": answer,
        "sources": documents
    }
