import copy
from typing import Dict

from backend.services.matcher import (
    match_experience_section,
    match_project_section,
)


# -----------------------------
# Tailoring Engine
# -----------------------------
def tailor_resume(
    resume_json: Dict,
    jd_keywords: Dict,
) -> Dict:
    """
    Assemble a tailored resume JSON using deterministic logic.
    - No rewriting
    - No hallucination
    - Preserve original content
    """

    if not resume_json:
        raise ValueError("Resume JSON is empty")

    if not jd_keywords:
        raise ValueError("JD keywords are empty")

    # Deep copy to avoid mutating original resume
    tailored = copy.deepcopy(resume_json)

    # -----------------------------
    # Experience Section
    # -----------------------------
    experience = tailored.get("Work Experience", [])
    if experience:
        tailored["Work Experience"] = match_experience_section(
            experience=experience,
            jd_keywords=jd_keywords,
            max_bullets=4
        )

    # -----------------------------
    # Project Section
    # -----------------------------
    projects = tailored.get("Project Experience", [])
    if projects:
        tailored["Project Experience"] = match_project_section(
            projects=projects,
            jd_keywords=jd_keywords,
            max_bullets=2
        )

    # -----------------------------
    # Skills Section (Reordering only)
    # -----------------------------
    skills = tailored.get("Skills", [])
    if skills:
        jd_terms = {
            term.lower()
            for values in jd_keywords.values()
            for term in values
        }

        # Prioritize JD-matching skills
        matched = []
        others = []

        for skill in skills:
            if skill.lower() in jd_terms:
                matched.append(skill)
            else:
                others.append(skill)

        tailored["Skills"] = matched + others

    return tailored
