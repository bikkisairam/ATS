import json
import os
from pathlib import Path

import google.generativeai as genai
from docx import Document
import PyPDF2

from backend.config import Config


# -----------------------------
# Gemini Setup
# -----------------------------
Config.validate()
genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


# -----------------------------
# Resume Readers
# -----------------------------
def _read_docx(path: Path) -> str:
    doc = Document(path)
    return "\n".join(
        p.text.strip() for p in doc.paragraphs if p.text.strip()
    )


def _read_pdf(path: Path) -> str:
    text = []
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)


def extract_resume_text(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Resume not found: {file_path}")

    if path.suffix.lower() == ".docx":
        return _read_docx(path)
    elif path.suffix.lower() == ".pdf":
        return _read_pdf(path)
    else:
        raise ValueError("Unsupported resume format. Use .docx or .pdf")


# -----------------------------
# Gemini → JSON Converter
# -----------------------------
def resume_to_json(resume_text: str) -> dict:
    """
    Converts resume text into a strict JSON schema.
    Gemini is used ONLY for structuring, not rewriting.
    """

    prompt = f"""
    Convert the following resume into JSON using EXACTLY this schema:

    {{
      "Details": {{
        "Name": "",
        "Email": "",
        "Phone": "",
        "Location": "",
        "LinkedIn": "",
        "GitHub": ""
      }},
      "Summary": "",
      "Skills": [],
      "Work Experience": [
        {{
          "Company Name": "",
          "Role": "",
          "Bullet Points": [],
          "Date": ""
        }}
      ],
      "Project Experience": [
        {{
          "Title": "",
          "Bullet Points": [],
          "Tech Stack": ""
        }}
      ],
      "Education": [
        {{
          "Institution": "",
          "Degree": "",
          "Date": ""
        }}
      ],
      "Achievements and Certifications": []
    }}

    Rules (VERY IMPORTANT):
    - Preserve text exactly as written (do NOT rewrite).
    - Do NOT invent content.
    - Do NOT add metrics or technologies.
    - If information is missing, use "" or [].
    - Bullet points must be plain text (no symbols like • or -).
    - Output ONLY valid JSON. No markdown. No explanation.

    Resume:
    {resume_text}
    """

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Remove accidental markdown fences
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError("Gemini returned invalid JSON") from e

    return parsed


# -----------------------------
# Public API
# -----------------------------
def parse_resume(file_path: str) -> dict:
    """
    High-level function used by the API.
    """
    text = extract_resume_text(file_path)
    return resume_to_json(text)
