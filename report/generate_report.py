
import json
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Image, Table, TableStyle, KeepTogether
)

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "report"
summary = json.loads(
    (ROOT / "evaluation" / "summary.json").read_text()
)

output = REPORT / "Canadian_Cybersecurity_RAG_Final_Report.pdf"

styles = getSampleStyleSheet()
story = []

def heading(text):
    story.append(Spacer(1, 12))
    story.append(Paragraph(text, styles["Heading2"]))

def paragraph(text):
    story.append(Paragraph(text, styles["BodyText"]))
    story.append(Spacer(1, 8))

def screenshot(filename, caption):
    path = REPORT / filename
    if not path.exists():
        return
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(470 / w, 300 / h)
    story.append(KeepTogether([
        Image(str(path), width=w * scale, height=h * scale),
        Spacer(1, 5),
        Paragraph(caption, styles["Caption"] if "Caption" in styles else styles["BodyText"]),
    ]))
    story.append(Spacer(1, 12))

story.append(Paragraph(
    "Canadian Cybersecurity RAG - Final Project Report",
    styles["Title"]
))
paragraph("Data Mining | Vanier College | Fall 2026")

heading("1. Project Objective")
paragraph(
    "Build a retrieval-augmented generation system that answers "
    "cybersecurity questions using retrieved reference documents."
)

heading("2. Dataset and Preprocessing")
paragraph(
    "The corpus includes 99 OWASP Cheat Sheet Series Markdown documents "
    "and one additional cybersecurity basics text document: 100 documents "
    "in total. OWASP guidance is not Canadian government guidance."
)
paragraph(
    "Documents were split into overlapping chunks of 900 characters "
    "with 150-character overlap. Sentence embeddings were generated "
    "using all-MiniLM-L6-v2 and stored in ChromaDB. "
    "The collection contains 2,599 indexed chunks."
)

heading("3. RAG Architecture")
steps = [
    "User question",
    "Sentence-transformer query embedding",
    "ChromaDB similarity search: top 3 chunks",
    "Retrieved context + system prompt + question",
    "Ollama with Qwen2.5:3b",
    "Generated answer + source excerpts",
    "Langfuse tracing and evaluation",
]
diagram = Table([[step] for step in steps], colWidths=[450])
diagram.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF2FA")),
    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#315777")),
    ("INNERGRID", (0, 0), (-1, -1), 1, colors.white),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("TOPPADDING", (0, 0), (-1, -1), 9),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
]))
story.append(diagram)

heading("4. Implementation")
paragraph(
    "The application uses FastAPI with /health and /query endpoints. "
    "The retrieval pipeline searches ChromaDB and passes the retrieved "
    "context to the language model. Local end-to-end generation "
    "was successfully tested using Ollama and Qwen2.5:3b."
)
paragraph(
    "A Gemini client was implemented, but API credit restrictions "
    "prevented successful Gemini generation."
)

heading("5. Evaluation")
paragraph(
    "Ten cybersecurity questions were tested, each with one expected "
    "source document. Expected-source hit rate@3 measures whether "
    "the expected document appeared among the top three results. "
    "Answers were reviewed qualitatively against retrieved excerpts."
)

rows = [
    ["Metric", "Result"],
    ["Documents", "100"],
    ["Indexed chunks", "2,599"],
    ["Expected-source hit rate@3", "90% (9/10)"],
    ["Generated answers", "10/10"],
    ["Grounded", str(summary["grounded"])],
    ["Grounded with limitations", str(summary["grounded_with_limitations"])],
    ["Mostly grounded", str(summary["mostly_grounded"])],
    ["Partially grounded", str(summary["partially_grounded"])],
]
table = Table(rows, colWidths=[300, 150], repeatRows=1)
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#244567")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
     [colors.white, colors.HexColor("#F0F4F8")]),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]))
story.append(table)

paragraph(
    "The authentication question missed its expected source at top 3. "
    "Some answers contained tangential guidance or repetition. "
    "This qualitative review was not a sentence-level factual audit."
)

heading("6. Langfuse Observability")
paragraph(
    "Langfuse captured RAG query and retrieval traces. "
    "The following screenshots document tracing activity."
)
screenshot("langfuse_rag_query.png", "Figure 1. RAG query trace.")
screenshot("langfuse_tracing.png", "Figure 2. Langfuse tracing overview.")

heading("7. Google Cloud Deployment")
paragraph(
    "A Docker image was built and pushed to Google Artifact Registry. "
    "A private Cloud Run service was deployed, and its /health endpoint "
    "returned a healthy status. The cloud /query endpoint was not "
    "successfully demonstrated because the deployed Gemini path "
    "encountered API credit restrictions. Local Ollama is not "
    "available to the Cloud Run service. Cloud deployment is partial."
)

heading("8. Limitations and Future Work")
paragraph(
    "Limitations include a small evaluation set, qualitative grounding "
    "assessment, occasional retrieval of tangential documents, and "
    "incomplete cloud-hosted generation. Future work includes improved "
    "retrieval ranking, larger evaluation sets, automated groundedness "
    "checks, and a cloud-accessible language model."
)

heading("9. Repository")
paragraph(
    "https://github.com/nt-mk/Canadian-Cybersecurity-RAG"
)

heading("10. AI Use Disclosure")
paragraph(
    "AI assistance supported coding, debugging, evaluation scripts, "
    "and documentation drafting. Reported experimental results are "
    "based on saved project outputs. The student is responsible "
    "for reviewing and submitting the work."
)

doc = SimpleDocTemplate(
    str(output),
    pagesize=A4,
    leftMargin=48,
    rightMargin=48,
    topMargin=48,
    bottomMargin=48,
)
doc.build(story)

print("PDF_CREATED:", output)
print("PDF_SIZE_BYTES:", output.stat().st_size)
