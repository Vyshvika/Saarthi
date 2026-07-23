"""
LLM-as-judge signal detection, meant to sit next to (or eventually replace)
the keyword matcher in prompts.py.

Uses the existing generate_reply() wrapper from llm_client.py, so it goes
through the same Groq call path already used for chat replies. Nothing new
to configure beyond the .env you already have.

This module could not be executed inside the sandbox used to build the rest
of this evaluation (the sandbox's network allowlist does not include Groq's
API), so these numbers are not included in results.json. Run judge_eval.py
locally once you drop this file into backend/ to get a second set of
precision/recall/F1 numbers for the comparison table in your paper.
"""
import json
from llm_client import generate_reply

JUDGE_SYSTEM_PROMPT = (
    "You are a classifier, not a tutor. You will be shown a single student message "
    "from a tutoring chat. Decide whether the message expresses genuine confusion "
    "about what was just explained, genuine advanced/mastery-level curiosity, or "
    "neither. Respond with ONLY a JSON object, no other text, in the exact form: "
    '{"label": "confusion" | "mastery" | "neutral", "confidence": 0.0-1.0}'
)


def judge_message(student_message: str) -> dict:
    """
    Returns {"label": "confusion"|"mastery"|"neutral", "confidence": float}.
    Falls back to neutral/0.0 on any parse failure so a bad judge call never
    crashes the recalibration flow.
    """
    raw = generate_reply(
        JUDGE_SYSTEM_PROMPT,
        [{"role": "user", "content": student_message}],
    )
    try:
        cleaned = raw.strip().strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
        parsed = json.loads(cleaned)
        label = parsed.get("label", "neutral")
        confidence = float(parsed.get("confidence", 0.0))
        if label not in ("confusion", "mastery", "neutral"):
            label = "neutral"
        return {"label": label, "confidence": confidence}
    except Exception:
        return {"label": "neutral", "confidence": 0.0}


# --- Suggested integration point in chat_router.py ---
#
# from llm_judge import judge_message
#
# judge_result = judge_message(req.content)
# use_confusion = detect_confusion(req.content) or judge_result["label"] == "confusion"
# use_mastery = detect_mastery_signal(req.content) or judge_result["label"] == "mastery"
#
# then pass a small wrapper into recalibrate() that uses use_confusion/use_mastery
# instead of re-running the raw keyword functions internally. The cleanest change
# is to split recalibrate() into a version that accepts pre-computed confused/advanced
# booleans, so the keyword and LLM-judge paths share the same streak/threshold logic.
