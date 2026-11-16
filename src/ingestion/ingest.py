from pathlib import Path
import argparse
import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "chroma_db"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def read_document(path):
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")

def split_text(text, chunk_size=900, overlap=150):
    text = " ".join(text.split())
    step = chunk_size - overlap
    return [
        text[i:i + chunk_size]
        for i in range(0, len(text), step)
        if len(text[i:i + chunk_size]) >= 30
    ]

def ingest(input_dir):
    folder = Path(input_dir)
    files = sorted(
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in {".txt", ".md", ".pdf"}
    )

    if not files:
        raise RuntimeError("No supported documents found.")

    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=str(DB_PATH))
    collection = client.get_or_create_collection("cybersecurity_docs")

    ids, documents, metadatas = [], [], []
    for path in files:
        chunks = split_text(read_document(path))
        for i, chunk in enumerate(chunks):
            ids.append(f"{path.stem}_{i}")
            documents.append(chunk)
            metadatas.append({"source": path.name, "chunk": i})

    embeddings = model.encode(documents, normalize_embeddings=True).tolist()
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"Documents: {len(files)}")
    print(f"Chunks indexed: {len(ids)}")
    print(f"ChromaDB location: {DB_PATH}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default=str(ROOT / "data/raw"))
    args = parser.parse_args()
    ingest(args.input_dir)
