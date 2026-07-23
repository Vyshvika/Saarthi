# Saarthi — an adaptive-calibration tutoring guide

Saarthi is a chat-based tutoring platform that calibrates how it explains things to
match the learner, and keeps adjusting through the conversation instead of relying
on a single, static self-assessment.

## Why this is different from a plain "difficulty setting"

Most adaptive-tutor demos ask a student to pick a level once, store it as a flag,
and use that flag to swap out a paragraph template. That's a UI feature, not an
adaptive system.

Saarthi treats the student's chosen track (Foundation / Growth / Mastery) as a
**starting point, not a fixed setting**. During the conversation, a lightweight
signal detector watches for:

- **Confusion signals** — phrases like "I don't get it", "explain again", "in
  simpler terms" — which step the guide's effective level down one notch after
  two consecutive occurrences.
- **Mastery signals** — phrases like "can you prove that", "what's the time
  complexity", "edge case" — which step the effective level up one notch.

Every adjustment is logged against the message it was triggered by (`level_at_response`,
`confusion_signal`, `mastery_signal`, `response_latency_ms` in the `messages` table),
which gives you a genuine evaluation dataset rather than just a demo:

- **Adaptation accuracy** — did a confusion signal actually correspond to a level drop
  that resolved the confusion (i.e., no confusion signal in the next 1-2 turns)?
- **Level stability** — how often does the effective level oscillate versus settle?
- **Time-to-clarity** — turns elapsed between a confusion signal and the next
  message with no confusion/mastery signal.
- **Response latency by level** — do more detailed (Foundation) responses take
  meaningfully longer to generate/stream?

These give you real charts and numbers for a results section, rather than only
screenshots of the UI.

## Structure

- `backend/` — FastAPI service: auth, session + message persistence, the
  calibration logic (`prompts.py`), and a vendor-neutral LLM wrapper (`llm_client.py`).
- `frontend/` — React + Vite chat interface with a calibration-dial signature
  element in the header that reflects the session's current effective level.

## Running it locally

See `backend/README.md` and `frontend/README.md`. In short: start the backend on
port 8000, then the frontend on port 5173 (it proxies `/api` to the backend).

## Suggested framing for a paper

Position the contribution as **within-session adaptive calibration for LLM-based
tutoring**, not "a chatbot with a difficulty setting." The novel part is the
signal-driven recalibration loop and the audit trail it produces, which is what
you'd evaluate and report on.
