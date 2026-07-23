"""
Adaptive calibration layer.

Maps a student's track (foundation / growth / mastery) to a distinct
teaching style, and detects in-conversation signals that suggest the
current calibration is wrong for this moment - so the guide can drift
up or down without the student ever re-configuring anything.
"""

LEVEL_PROMPTS = {
    "foundation": (
        "You are a patient, encouraging tutor working with a student who is building "
        "confidence in this subject from the ground up. Never assume prior knowledge, "
        "even of terms that seem basic - define every new term the moment you use it. "
        "Break every explanation into the smallest possible steps, using one idea per "
        "sentence. Use concrete, everyday analogies (cooking, money, distances, sports) "
        "before introducing any abstract notation. After explaining a concept, restate "
        "it once more in plain words. Never say 'as you know' or 'obviously'. Keep a "
        "warm, unhurried tone - the student should never feel rushed or judged for "
        "asking something simple."
    ),
    "growth": (
        "You are a clear, structured tutor working with a student who has a working "
        "grasp of the basics and wants to go deeper. Explain concepts with proper "
        "structure: a short definition, then a worked example, then one common pitfall "
        "to watch for. Use precise terminology but briefly define anything non-obvious "
        "the first time it appears. Favor clarity and completeness over brevity - the "
        "student wants to genuinely understand the mechanism, not just get an answer."
    ),
    "mastery": (
        "You are a sharp, direct technical peer working with a strong student. Skip "
        "basic definitions and setup - get straight to the substance. Be concise and "
        "precise, use correct terminology without hedging, and where relevant surface "
        "edge cases, trade-offs, or the 'why' behind a result rather than just the "
        "'what'. Treat the student as capable of following dense reasoning."
    ),
}

LEVEL_ORDER = ["foundation", "growth", "mastery"]

CONFUSION_MARKERS = [
    "don't understand", "dont understand", "not clear", "i'm confused", "im confused",
    "what does that mean", "what do you mean", "can you explain again", "still confused",
    "makes no sense", "i don't get it", "i dont get it", "huh", "wait what", "too fast",
    "in simpler terms", "like i'm five", "like im five", "in simple words",
]

MASTERY_MARKERS = [
    "can you prove", "derive", "edge case", "time complexity", "space complexity",
    "what's the trade-off", "whats the tradeoff", "optimize", "under the hood",
    "formal definition", "counter-example", "counterexample", "asymptotic",
]


def detect_confusion(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in CONFUSION_MARKERS)


def detect_mastery_signal(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in MASTERY_MARKERS)


def step_level(current_level: str, direction: int) -> str:
    """Move one step up (+1) or down (-1) along the level order, clamped at the ends."""
    idx = LEVEL_ORDER.index(current_level)
    new_idx = max(0, min(len(LEVEL_ORDER) - 1, idx + direction))
    return LEVEL_ORDER[new_idx]


def recalibrate(effective_level: str, confusion_streak: int, mastery_streak: int, user_message: str):
    """
    Given the current session state and the student's latest message, decide whether
    the effective level should drift. Two consecutive confusion signals step the level
    down one notch; two consecutive mastery signals step it up one notch. Streaks reset
    whenever the opposing signal fires.

    Returns: (new_effective_level, new_confusion_streak, new_mastery_streak, adjusted: bool)
    """
    confused = detect_confusion(user_message)
    advanced = detect_mastery_signal(user_message)

    if confused:
        confusion_streak += 1
        mastery_streak = 0
    elif advanced:
        mastery_streak += 1
        confusion_streak = 0
    else:
        # a neutral message doesn't erase a streak outright, but softens it
        confusion_streak = max(0, confusion_streak - 1)
        mastery_streak = max(0, mastery_streak - 1)

    adjusted = False
    new_level = effective_level

    if confusion_streak >= 2:
        stepped = step_level(effective_level, -1)
        if stepped != effective_level:
            new_level = stepped
            adjusted = True
        confusion_streak = 0

    elif mastery_streak >= 2:
        stepped = step_level(effective_level, +1)
        if stepped != effective_level:
            new_level = stepped
            adjusted = True
        mastery_streak = 0

    return new_level, confusion_streak, mastery_streak, adjusted
