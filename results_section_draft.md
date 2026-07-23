# Evaluation

## Method

We evaluated the recalibration layer against a hand-labeled synthetic conversation
set: 15 scripted multi-turn conversations (61 turns total, spanning all three
tracks) written to cover confusion, mastery, and neutral student intent. Each turn
was labeled with its true intent independent of surface wording. About a third of
the confusion/mastery turns were phrased as paraphrases rather than using any of
the system's exact trigger phrases (e.g. "none of that landed for me" instead of
"I don't understand"), so the evaluation would expose realistic detection gaps
rather than only testing the keyword list against itself. This is a synthetic,
hand-labeled evaluation set, not logged data from real student sessions; we treat
it as a controlled test of the recalibration logic rather than a user study.

The recalibrate(), detect_confusion(), and detect_mastery_signal() functions used
in the evaluation are the exact functions shipped in the production system
(prompts.py), run directly rather than reimplemented for testing.

## Signal detection performance

| | Precision | Recall | F1 |
|---|---|---|---|
| Confusion detection | 1.00 | 0.79 | 0.88 |
| Mastery detection | 1.00 | 0.64 | 0.78 |

Overall accuracy across all 61 turns was 0.93 for both signal types. Precision was
perfect for both classes: the keyword matcher never raised a false alarm. Recall
is where it breaks down, and the gap tracks phrasing directly:

| | Precision | Recall | F1 |
|---|---|---|---|
| Exact marker phrasing | 1.00 | 1.00 | 1.00 |
| Paraphrased, no exact marker | 1.00 | 0.20 | 0.33 |

When a student's message contains one of the system's exact trigger phrases,
detection is perfect. When the same intent is phrased differently, recall drops to
0.20. This is the concrete version of the review concern raised earlier: a student
who is confused but doesn't happen to use one of the listed phrases will not be
detected, and the effective level will not adjust for them.

## Adaptation behavior vs. a static baseline

Of the 9 genuine two-turn-or-longer confusion streaks in the dataset, the adaptive
system resolved 4 (44%) with an actual level drop. A static baseline, where the
level is fixed at signup and never adjusts, resolves 0 by construction. So on this
dataset, adaptive recalibration catches under half of real confusion streaks, but
a fixed-level system catches none of them. That comparison, not a claim of overall
accuracy, is the honest way to state the current result: the mechanism works when
it fires, but its coverage is limited by the same keyword-recall problem shown
above.

Across conversations that did produce a level change, the average was 0.4 changes
per conversation (max 2), and no session oscillated back and forth more than once
in either direction, which is consistent with the two-in-a-row threshold behaving
as designed rather than reacting to noise.

## Limitation and next step

The dominant failure mode is recall on paraphrased signals, not precision. This
motivates replacing or augmenting the keyword matcher with an LLM-as-judge step
(a lightweight follow-up call asking whether the last response likely landed),
which is the natural next iteration and does not require changing the
recalibration or logging logic, only the signal source feeding it.
