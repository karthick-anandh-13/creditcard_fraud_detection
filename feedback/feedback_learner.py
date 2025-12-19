import json
from pathlib import Path
from collections import deque
from storage.risk_profile_repo import RiskProfileStore
from state.threshold_controller import tighten_thresholds, relax_thresholds

BASE_DIR = Path(__file__).resolve().parent.parent
FEEDBACK_FILE = BASE_DIR / "feedback" / "data" / "fraud_feedback.log"

WINDOW = 50

def apply_online_learning():
    if not FEEDBACK_FILE.exists():
        return

    recent = deque(maxlen=WINDOW)

    with open(FEEDBACK_FILE) as f:
        for line in f:
            recent.append(json.loads(line))

    if len(recent) < 10:
        return

    store = RiskProfileStore()

    fn = fp = 0
    for r in recent:
        if r["final_decision"] == "ALLOW" and r["actual_outcome"] == "FRAUD":
            fn += 1
        if r["final_decision"] == "BLOCK" and r["actual_outcome"] == "GENUINE":
            fp += 1

    fn_rate = fn / len(recent)
    fp_rate = fp / len(recent)

    for r in recent:
        profile = store.col.find_one({"payer_vpa": r["payer_vpa"]})
        if not profile:
            continue

        if fn_rate > 0.08:
            tighten_thresholds(profile)
        elif fp_rate > 0.10:
            relax_thresholds(profile)

        store.col.update_one(
            {"payer_vpa": profile["payer_vpa"]},
            {"$set": {
                "block_threshold": profile["block_threshold"],
                "step_up_threshold": profile["step_up_threshold"]
            }}
        )
