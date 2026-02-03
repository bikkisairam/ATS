import re
from typing import List, Dict, Tuple


# -----------------------------
# Text Utilities
# -----------------------------
def _normalize(text: str) -> List[str]:
    """
    Lowercase, remove symbols, split into tokens.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if len(t) > 1]


def _keyword_set(jd_keywords: Dict[str, List[str]]) -> set:
    """
    Combine all JD keywords into a single searchable set.
    """
    combined = set()
    for values in jd_keywords.values():
        for v in values:
            for token in _normalize(v):
                combined.add(token)
    return combined


# -----------------------------
# Bullet Scoring
# -----------------------------
def score_bullet(bullet: str, jd_terms: set) -> int:
    """
    Score a bullet based on keyword overlap with JD terms.
    """
    bullet_tokens = set(_normalize(bullet))
    return len(bullet_tokens.intersection(jd_terms))


def rank_bullets(
    bullets: List[str],
    jd_keywords: Dict[str, List[str]]
) -> List[Tuple[str, int]]:
    """
    Rank bullets by relevance score.
    Returns list of (bullet, score), sorted descending.
    """
    jd_terms = _keyword_set(jd_keywords)

    scored = []
    for bullet in bullets:
        score = score_bullet(bullet, jd_terms)
        scored.append((bullet, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


# -----------------------------
# Resume Section Matching
# -----------------------------
def match_experience_section(
    experience: List[Dict],
    jd_keywords: Dict[str, List[str]],
    max_bullets: int = 4
) -> List[Dict]:
    """
    Select and reorder bullets for each job based on relevance.
    No rewriting. No invention.
    """
    updated_experience = []

    for job in experience:
        bullets = job.get("Bullet Points", [])
        ranked = rank_bullets(bullets, jd_keywords)

        # Keep top N bullets, preserve text
        selected = [b for b, _ in ranked[:max_bullets]]

        updated_experience.append({
            **job,
            "Bullet Points": selected
        })

    return updated_experience


def match_project_section(
    projects: List[Dict],
    jd_keywords: Dict[str, List[str]],
    max_bullets: int = 3
) -> List[Dict]:
    """
    Select and reorder project bullets based on relevance.
    """
    updated_projects = []

    for project in projects:
        bullets = project.get("Bullet Points", [])
        ranked = rank_bullets(bullets, jd_keywords)

        selected = [b for b, _ in ranked[:max_bullets]]

        updated_projects.append({
            **project,
            "Bullet Points": selected
        })

    return updated_projects
