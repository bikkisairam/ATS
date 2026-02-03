import json
import google.generativeai as genai
from typing import Dict, List

from backend.config import Config


# -----------------------------
# Gemini Setup
# -----------------------------
Config.validate()
genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


# -----------------------------
# JD Keyword Extraction
# -----------------------------
def extract_jd_keywords(jd_text: str) -> Dict[str, List[str]]:
    """
    Extract structured keywords from a job description.
    Gemini is used ONLY for extraction, never for rewriting.
    """

    if not jd_text or not jd_text.strip():
        raise ValueError("Job description text is empty")

    prompt = f"""
    You are an ATS analyst.

    Extract information from the job description below and return
    ONLY valid JSON using this exact schema:

    {{
      "required_skills": [],
      "preferred_skills": [],
      "tools_and_technologies": [],
      "domains": [],
      "keywords": []
    }}

    Rules (STRICT):
    - Do NOT invent skills or tools.
    - Use words exactly as they appear in the job description.
    - Keep items short (1–3 words).
    - No explanations, no markdown.
    - Output ONLY valid JSON.

    Job Description:
    {jd_text}
    """

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Remove accidental markdown fences
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError("Gemini returned invalid JSON for JD extraction") from e

    # Safety normalization
    for key in [
        "required_skills",
        "preferred_skills",
        "tools_and_technologies",
        "domains",
        "keywords",
    ]:
        data.setdefault(key, [])
        if not isinstance(data[key], list):
            data[key] = []

    return data
