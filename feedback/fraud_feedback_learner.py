import json
from pathlib import Path

from storage.risk_profile_repo import RiskProfileStore
from state.threshold_controller import adjust_global_thresholds


BASE_DIR = Path(__file__).resolve().parent.parent
FEEDBACK_FILE = BASE_DIR / "feedback" / "data" / "fraud_feedback.log"

risk_store = RiskProfileStore()

def learn_from_feedback():
    if not FEEDBACK_FILE.exists():
        print("No feedback available")
        return

    with open(FEEDBACK_FILE, "r") as f:
        for line in f:
            record = json.loads(line)

            payer = record["payer_vpa"]
            decision = record["final_decision"]
            actual = record["actual_outcome"]

            # ❌ Fraud slipped through
            if decision == "ALLOW" and actual == "FRAUD":
               risk_store.tighten_user_thresholds(payer)
               adjust_global_thresholds("FRAUD_LEAKAGE")

            elif decision == "BLOCK" and actual == "GENUINE":
                risk_store.relax_user_thresholds(payer)
                adjust_global_thresholds("CUSTOMER_FRICTION")
                print("[FEEDBACK LEARNING] completed")

if __name__ == "__main__":
    learn_from_feedback()
