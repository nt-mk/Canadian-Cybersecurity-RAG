import os
import time
from google.genai.errors import ServerError
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def generate_answer(question: str, context: str) -> str:
    client = genai.Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0227281842"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "global"),
        http_options=types.HttpOptions(timeout=15000),
    )

    for attempt in range(3):
        try:
            response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a cybersecurity education assistant. "
                "Answer only using the retrieved context. "
                "If the context is insufficient, say: "
                "'Not enough information in the provided documents.' "
                "Do not invent facts."
            ),
            temperature=0.2,
        ),
        contents=(
            f"Retrieved context:\n{context}\n\n"
            f"User question:\n{question}"
        ),
    )
            return response.text or "No response generated."
        except ServerError as e:
            if e.code != 503 or attempt == 2:
                raise
            time.sleep(2 ** (attempt + 1))
