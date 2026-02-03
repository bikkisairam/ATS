import re
from typing import List, Dict


# -----------------------------
# Utility Extractors
# -----------------------------
def _extract_numbers(text: str) -> set:
    return set(re.findall(r"\b\d+(\.\d+)?\b", text))


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


# -----------------------------
# Hallucination Checks
# -----------------------------
def detect_new_numbers(original: List[str], modified: List[str]) -> bool:
    """
    Detect if modified bullets introduced new numeric claims.
    """
    orig_nums = set()
    for b in original:
        orig_nums |= _extract_numbers(b)

    mod_nums = set()
    for b in modified:
        mod_nums |= _extract_numbers(b)

    return not mod_nums.issubset(orig_nums)


def detect_new_bullets(original: List[str], modified: List[str]) -> bool:
    """
    Detect if new bullet text appears that didn't exist before.
    """
    orig_norm = {_normalize(b) for b in original}
    for b in modified:
        if _normalize(b) not in orig_norm:
            return True
    return False


# -----------------------------
# Section Guard
# -----------------------------
def guard_bullets(
    original_bullets: List[str],
    modified_bullets: List[str],
) -> List[str]:
    """
    Validate bullets. If hallucination detected, fallback to original bullets.
    """
    if detect_new_numbers(original_bullets, modified_bullets):
        return original_bullets

    if detect_new_bullets(original_bullets, modified_bullets):
        return original_bullets

    return modified_bullets


# -----------------------------
# Resume Guard
# -----------------------------
def guard_resume(
    original_resume: Dict,
    modified_resume: Dict,
) -> Dict:
    """
    Apply hallucination guards to experience and project sections.
    """
    guarded = modified_resume.copy()

    # Work Experience
    for idx, job in enumerate(modified_resume.get("Work Experience", [])):
        orig_job = original_resume.get("Work Experience", [])[idx]

        guarded["Work Experience"][idx]["Bullet Points"] = guard_bullets(
            original_bullets=orig_job.get("Bullet Points", []),
            modified_bullets=job.get("Bullet Points", []),
        )

    # Project Experience
    for idx, proj in enumerate(modified_resume.get("Project Experience", [])):
        orig_proj = original_resume.get("Project Experience", [])[idx]

        guarded["Project Experience"][idx]["Bullet Points"] = guard_bullets(
            original_bullets=orig_proj.get("Bullet Points", []),
            modified_bullets=proj.get("Bullet Points", []),
        )

    return guarded
