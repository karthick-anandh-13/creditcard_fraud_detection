import json
from pathlib import Path
from collections import deque

from state.threshold_controller import adjust_global_thresholds

BASE_DIR = Path(__file__).resolve().parent.parent
FEEDBACK_FILE = BASE_DIR / "feedback" / "data" / "fraud_feedback.log"

WINDOW_SIZE = 100

def detect_drift():
    if not FEEDBACK_FILE.exists():
        print("No feedback data yet")
        return

    recent = deque(maxlen=WINDOW_SIZE)

    with open(FEEDBACK_FILE, "r") as f:
        for line in f:
            recent.append(json.loads(line))

    if len(recent) < 20:
        print("Not enough data for drift detection")
        return

    false_negatives = 0
    false_positives = 0

    for r in recent:
        decision = r["final_decision"]
        actual = r["actual_outcome"]

        if decision == "ALLOW" and actual == "FRAUD":
            false_negatives += 1

        if decision == "BLOCK" and actual == "GENUINE":
            false_positives += 1

    fn_rate = false_negatives / len(recent)
    fp_rate = false_positives / len(recent)

    print(f"[DRIFT CHECK] FN={fn_rate:.2%} | FP={fp_rate:.2%}")

    # 🚨 System-wide learning
    if fn_rate > 0.08:
        adjust_global_thresholds("FRAUD_LEAKAGE")

    elif fp_rate > 0.10:
        adjust_global_thresholds("CUSTOMER_FRICTION")


if __name__ == "__main__":
    detect_drift()
