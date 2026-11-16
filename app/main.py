from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.rag_pipeline import answer_question

app = FastAPI(title="Canadian Cybersecurity RAG API")

class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/query")
def query(request: QueryRequest):
    try:
        return answer_question(request.question, request.top_k)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"RAG service unavailable: {type(exc).__name__}"
        )
