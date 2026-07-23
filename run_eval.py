"""
Evaluation runner for Saarthi's recalibration layer.

Uses the REAL recalibrate() / detect_confusion() / detect_mastery_signal()
functions copied verbatim from backend/prompts.py - not reimplemented - so the
numbers reflect the actual shipped logic.

Writes results to a fresh sqlite db (saarthi_eval.db), separate from the
production saarthi.db, since this is a synthetic hand-labeled evaluation set,
not real user activity. Keeping it separate means the production database
still only contains genuine usage.
"""
import sqlite3
import json
import os
from prompts import recalibrate, detect_confusion, detect_mastery_signal, LEVEL_ORDER
from backend.eval_dataset import CONVERSATIONS

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(OUT_DIR, "saarthi_eval.db")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""
CREATE TABLE eval_turns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER,
    turn_index INTEGER,
    base_level TEXT,
    text TEXT,
    ground_truth_label TEXT,
    on_marker INTEGER,
    detected_confusion INTEGER,
    detected_mastery INTEGER,
    predicted_label TEXT,
    adaptive_level_before TEXT,
    adaptive_level_after TEXT,
    adaptive_adjusted INTEGER,
    static_level TEXT
)
""")

rows = []
for conv_id, conv in enumerate(CONVERSATIONS):
    base = conv["base_level"]
    level = base
    c_streak = 0
    m_streak = 0
    for turn_idx, (text, gt_label, on_marker) in enumerate(conv["turns"]):
        det_conf = detect_confusion(text)
        det_mast = detect_mastery_signal(text)
        pred_label = "confusion" if det_conf else ("mastery" if det_mast else "neutral")

        level_before = level
        new_level, c_streak, m_streak, adjusted = recalibrate(level, c_streak, m_streak, text)
        level = new_level

        rows.append((
            conv_id, turn_idx, base, text, gt_label,
            int(bool(on_marker)) if on_marker is not None else 0,
            int(det_conf), int(det_mast), pred_label,
            level_before, new_level, int(adjusted), base,  # static_level = base, never changes
        ))

cur.executemany("""
INSERT INTO eval_turns (
    conversation_id, turn_index, base_level, text, ground_truth_label, on_marker,
    detected_confusion, detected_mastery, predicted_label,
    adaptive_level_before, adaptive_level_after, adaptive_adjusted, static_level
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
""", rows)
conn.commit()

# ---------------------------------------------------------------------------
# Metric 1: signal-detection accuracy / precision / recall / F1
# ---------------------------------------------------------------------------
def binary_metrics(rows, gt_key, pred_key):
    tp = fp = fn = tn = 0
    for r in rows:
        gt = r[gt_key]
        pred = r[pred_key]
        if gt and pred:
            tp += 1
        elif pred and not gt:
            fp += 1
        elif gt and not pred:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    accuracy = (tp + tn) / (tp + fp + fn + tn) if (tp + fp + fn + tn) else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": precision, "recall": recall, "f1": f1, "accuracy": accuracy}

dicts = [dict(
    gt_confusion=(r[4] == "confusion"), gt_mastery=(r[4] == "mastery"),
    det_confusion=bool(r[6]), det_mastery=bool(r[7]),
    on_marker=bool(r[5]),
) for r in rows]

confusion_metrics = binary_metrics(dicts, "gt_confusion", "det_confusion")
mastery_metrics = binary_metrics(dicts, "gt_mastery", "det_mastery")

# same metrics, split by whether the turn used an exact marker phrase or a paraphrase
on_marker_rows = [d for d in dicts if d["on_marker"]]
paraphrase_rows = [d for d in dicts if not d["on_marker"] and (d["gt_confusion"] or d["gt_mastery"])]

def combined_signal_metrics(subset):
    tp = fp = fn = 0
    for d in subset:
        gt_signal = d["gt_confusion"] or d["gt_mastery"]
        pred_signal = d["det_confusion"] or d["det_mastery"]
        if gt_signal and pred_signal:
            tp += 1
        elif pred_signal and not gt_signal:
            fp += 1
        elif gt_signal and not pred_signal:
            fn += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}

exact_marker_perf = combined_signal_metrics(on_marker_rows)
paraphrase_perf = combined_signal_metrics(paraphrase_rows)

# ---------------------------------------------------------------------------
# Metric 2: adaptation behavior - does a qualifying confusion streak actually
# get resolved by a level drop, under adaptive vs a frozen static baseline?
# ---------------------------------------------------------------------------
def find_confusion_streaks(turns):
    """Ground-truth confusion streaks of length >= 2 (the system's trigger threshold)."""
    streaks = []
    run_start = None
    run_len = 0
    for i, (text, label, marker) in enumerate(turns):
        if label == "confusion":
            if run_start is None:
                run_start = i
            run_len += 1
        else:
            if run_len >= 2:
                streaks.append((run_start, run_start + run_len - 1))
            run_start = None
            run_len = 0
    if run_len >= 2:
        streaks.append((run_start, run_start + run_len - 1))
    return streaks

total_streaks = 0
resolved_adaptive = 0
level_changes_per_conv = []

for conv_id, conv in enumerate(CONVERSATIONS):
    conv_rows = [r for r in rows if r[0] == conv_id]
    streaks = find_confusion_streaks(conv["turns"])
    total_streaks += len(streaks)
    for (s, e) in streaks:
        # resolved if adaptive_adjusted fired on any turn within the streak, in the downward direction
        for idx in range(s, e + 1):
            r = conv_rows[idx]
            adjusted = r[11]
            lvl_before, lvl_after = r[9], r[10]
            if adjusted and LEVEL_ORDER.index(lvl_after) < LEVEL_ORDER.index(lvl_before):
                resolved_adaptive += 1
                break
    changes = sum(1 for r in conv_rows if r[11])
    level_changes_per_conv.append(changes)

adaptation_resolution_rate = resolved_adaptive / total_streaks if total_streaks else 0.0
# static baseline never adjusts, so by construction it resolves 0 of these streaks
static_resolution_rate = 0.0

avg_changes = sum(level_changes_per_conv) / len(level_changes_per_conv)
max_changes = max(level_changes_per_conv)
pct_conversations_with_any_change = sum(1 for c in level_changes_per_conv if c > 0) / len(level_changes_per_conv)

results = {
    "dataset_size": {
        "conversations": len(CONVERSATIONS),
        "turns": len(rows),
        "confusion_turns_gt": sum(1 for d in dicts if d["gt_confusion"]),
        "mastery_turns_gt": sum(1 for d in dicts if d["gt_mastery"]),
        "neutral_turns_gt": sum(1 for d in dicts if not d["gt_confusion"] and not d["gt_mastery"]),
    },
    "confusion_detection": confusion_metrics,
    "mastery_detection": mastery_metrics,
    "detector_performance_by_phrasing": {
        "exact_marker_phrasing": exact_marker_perf,
        "paraphrased_no_exact_marker": paraphrase_perf,
    },
    "adaptation_behavior": {
        "qualifying_confusion_streaks": total_streaks,
        "resolved_by_adaptive_system": resolved_adaptive,
        "adaptive_resolution_rate": adaptation_resolution_rate,
        "static_baseline_resolution_rate": static_resolution_rate,
        "avg_level_changes_per_conversation": avg_changes,
        "max_level_changes_in_a_conversation": max_changes,
        "pct_conversations_with_at_least_one_adjustment": pct_conversations_with_any_change,
    },
}

with open(os.path.join(OUT_DIR, "results.json"), "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
conn.close()
