import json
from pathlib import Path
from app.rag_pipeline import answer_question

questions = json.loads(Path("evaluation/questions.json").read_text())
results = []

for item in questions:
    response = answer_question(item["question"])
    results.append({
        "id": item["id"],
        "question": item["question"],
        "answer": response["answer"],
        "sources": response["sources"]
    })
    print(f"Q{item['id']:02d}: answer generated ({len(response['answer'])} chars)", flush=True)

Path("evaluation/answer_results.json").write_text(
    json.dumps(results, indent=2, ensure_ascii=False) + "\n"
)
print("SAVED: evaluation/answer_results.json")
