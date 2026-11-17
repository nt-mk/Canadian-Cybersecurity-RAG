import json
import os
from urllib.request import Request, urlopen

SYSTEM_PROMPT = (
    "You are a cybersecurity education assistant. "
    "Answer only using the retrieved context. "
    "If the context is insufficient, say: "
    "'Not enough information in the provided documents.' "
    "Do not invent facts."
)

def generate_answer(question: str, context: str) -> str:
    payload = json.dumps({
        "model": os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Retrieved context:\n{context}\n\nUser question:\n{question}"}
        ],
        "options": {"temperature": 0.2}
    }).encode("utf-8")

    request = Request(
        os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat"),
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urlopen(request, timeout=180) as response:
        result = json.load(response)

    return result["message"]["content"]
