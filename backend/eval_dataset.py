"""
Synthetic evaluation dataset for Saarthi's recalibration layer.

Each conversation is a scripted sequence of student turns. Every turn carries a
GROUND-TRUTH label (confusion / mastery / neutral) that reflects the student's
actual intent as written, NOT whether it happens to contain one of the exact
strings in CONFUSION_MARKERS / MASTERY_MARKERS. This is deliberate: about a third
of the confusion/mastery turns are phrased in ways a keyword matcher would miss
(paraphrases, indirect confusion, question forms), so the evaluation can surface
real detector weaknesses instead of trivially scoring 100%.

This is a hand-labeled synthetic set, not logged real-user data. State it that
way in the paper.
"""

# label: "confusion" | "mastery" | "neutral"
# on_marker: True if the turn uses one of the exact CONFUSION_MARKERS/MASTERY_MARKERS
#            strings (expected to be caught), False if it's a paraphrase/edge case
#            (a realistic miss for a keyword matcher).

CONVERSATIONS = [
    # ---- Foundation track: student stays confused, should drop... but is already at floor
    {
        "base_level": "foundation",
        "turns": [
            ("what is a variable", "neutral", None),
            ("i don't understand", "confusion", True),
            ("still confused, sorry", "confusion", True),
            ("ok that helps a bit", "neutral", None),
        ],
    },
    # ---- Growth track: genuine confusion via paraphrase (no exact marker), should still drop
    {
        "base_level": "growth",
        "turns": [
            ("can you explain recursion", "neutral", None),
            ("hmm none of that landed for me", "confusion", False),   # paraphrase, real confusion
            ("i'm lost, sorry, can we slow down", "confusion", False), # paraphrase
            ("ok i think i follow now", "neutral", None),
        ],
    },
    # ---- Growth track: exact-marker confusion, two in a row
    {
        "base_level": "growth",
        "turns": [
            ("what's a hash table", "neutral", None),
            ("i don't get it", "confusion", True),
            ("in simpler terms please", "confusion", True),
            ("got it, thanks", "neutral", None),
        ],
    },
    # ---- Growth track: advancing via exact markers, should rise to mastery
    {
        "base_level": "growth",
        "turns": [
            ("how does a binary search tree work", "neutral", None),
            ("what's the time complexity of that", "mastery", True),
            ("can you prove that bound", "mastery", True),
            ("interesting, what about deletion", "neutral", None),
        ],
    },
    # ---- Growth track: advancing via paraphrase (no exact marker), realistic miss
    {
        "base_level": "growth",
        "turns": [
            ("explain hashing", "neutral", None),
            ("yeah but why does that actually work under the surface", "mastery", False),
            ("is there a smarter way to do this than the obvious one", "mastery", False),
            ("cool, that's clearer", "neutral", None),
        ],
    },
    # ---- Mastery track: student is actually confused despite being on the mastery track
    {
        "base_level": "mastery",
        "turns": [
            ("walk me through the CAP theorem trade-offs", "neutral", None),
            ("wait what, that lost me completely", "confusion", True),
            ("i still don't understand the partition case", "confusion", False),
            ("ok clearer now", "neutral", None),
        ],
    },
    # ---- Mastery track: student pushes even further (should stay at ceiling)
    {
        "base_level": "mastery",
        "turns": [
            ("what's the asymptotic bound on this algorithm", "mastery", True),
            ("give me a formal definition and a counter-example", "mastery", True),
            ("nice, that tracks", "neutral", None),
        ],
    },
    # ---- Foundation track: single confusion signal only, should NOT drop (needs 2 in a row)
    {
        "base_level": "foundation",
        "turns": [
            ("what is a loop", "neutral", None),
            ("huh, not clear", "confusion", True),
            ("oh ok that makes sense now", "neutral", None),
            ("what happens after a loop finishes", "neutral", None),
        ],
    },
    # ---- Growth track: oscillation stress test (confusion then mastery back to back)
    {
        "base_level": "growth",
        "turns": [
            ("what is a linked list", "neutral", None),
            ("wait i don't understand pointers", "confusion", True),
            ("makes no sense to me still", "confusion", True),
            ("ok actually what's the time complexity of insertion then", "mastery", True),
            ("and can you derive why that's the case", "mastery", True),
        ],
    },
    # ---- Growth track: neutral-only conversation, no signals at all
    {
        "base_level": "growth",
        "turns": [
            ("what is object oriented programming", "neutral", None),
            ("can you give an example in python", "neutral", None),
            ("thanks that's useful", "neutral", None),
        ],
    },
    # ---- Foundation track: confusion phrased as a soft question (paraphrase miss)
    {
        "base_level": "foundation",
        "turns": [
            ("what is an array", "neutral", None),
            ("sorry, could you say that a different way, i'm not following", "confusion", False),
            ("that's still going over my head a bit", "confusion", False),
            ("ah ok i think i get it", "neutral", None),
        ],
    },
    # ---- Mastery track: paraphrased advanced question (miss)
    {
        "base_level": "mastery",
        "turns": [
            ("compare quicksort and mergesort", "neutral", None),
            ("what happens in the worst possible input you could construct", "mastery", False),
            ("is there a way to make this more efficient in practice", "mastery", False),
            ("good, that answers it", "neutral", None),
        ],
    },
    # ---- Growth track: single mastery signal only, should NOT rise (needs 2 in a row)
    {
        "base_level": "growth",
        "turns": [
            ("what is a stack", "neutral", None),
            ("what's the time complexity of push", "mastery", True),
            ("ok cool thanks", "neutral", None),
        ],
    },
    # ---- Foundation track: long neutral stretch then late confusion
    {
        "base_level": "foundation",
        "turns": [
            ("what is a function", "neutral", None),
            ("what is a parameter", "neutral", None),
            ("what is a return value", "neutral", None),
            ("i don't understand any of this anymore", "confusion", True),
            ("still confused", "confusion", True),
        ],
    },
    # ---- Growth track: confusion then recovery then confusion again
    {
        "base_level": "growth",
        "turns": [
            ("what is polymorphism", "neutral", None),
            ("i'm confused", "confusion", True),
            ("wait what", "confusion", True),
            ("ok that helped, thanks", "neutral", None),
            ("actually no, still not clear on inheritance", "confusion", False),
            ("yeah this makes no sense", "confusion", True),
        ],
    },
]
