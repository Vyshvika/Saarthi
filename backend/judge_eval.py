"""
Run this locally (inside backend/, with your .env and Groq key in place) to
get LLM-judge precision/recall/F1 on the same synthetic dataset used in
run_eval.py, for a direct comparison against the keyword matcher's numbers.

    cp eval_dataset.py llm_judge.py judge_eval.py backend/
    cd backend
    python judge_eval.py
"""
import json
from eval_dataset import CONVERSATIONS
from llm_judge import judge_message

rows = []
for conv_id, conv in enumerate(CONVERSATIONS):
    for turn_idx, (text, gt_label, on_marker) in enumerate(conv["turns"]):
        judged = judge_message(text)
        rows.append({
            "conversation_id": conv_id,
            "turn_index": turn_idx,
            "text": text,
            "ground_truth": gt_label,
            "judge_label": judged["label"],
            "judge_confidence": judged["confidence"],
        })
        print(f"[{conv_id}:{turn_idx}] gt={gt_label:10s} judge={judged['label']:10s} conf={judged['confidence']:.2f}  {text}")

def binary_metrics(rows, gt_value):
    tp = fp = fn = 0
    for r in rows:
        gt = r["ground_truth"] == gt_value
        pred = r["judge_label"] == gt_value
        if gt and pred:
            tp += 1
        elif pred and not gt:
            fp += 1
        elif gt and not pred:
            fn += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}

results = {
    "confusion_detection": binary_metrics(rows, "confusion"),
    "mastery_detection": binary_metrics(rows, "mastery"),
}
print("\n" + json.dumps(results, indent=2))
with open("judge_results.json", "w") as f:
    json.dump({"rows": rows, "metrics": results}, f, indent=2)
